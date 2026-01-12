"""Audio transcription service using SAP Generative AI Hub (Gemini 2.5 Flash)."""
from __future__ import annotations

import asyncio
import base64
import logging
from typing import Optional

from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel

from app.core.config import settings

logger = logging.getLogger(__name__)

_audio_proxy_client: Optional[object] = None
_audio_model: Optional[GenerativeModel] = None


def _resolve_audio_profile() -> tuple[dict[str, str], str]:
    """Return the AI Core profile to use for audio transcription."""

    instance = (settings.audio_model_instance or "US").strip().upper()
    if instance not in {"US", "JP"}:
        raise ValueError(
            "Unsupported AUDIO_MODEL_INSTANCE value. Use 'US' or 'JP'."
        )

    if instance == "US":
        profile = {
            "base_url": settings.aicore_base_url_us,
            "auth_url": settings.aicore_auth_url_us,
            "client_id": settings.aicore_client_id_us,
            "client_secret": settings.aicore_client_secret_us,
            "resource_group": settings.aicore_resource_group_us,
        }
        required_names = [
            ("AICORE_BASE_URL_US", profile["base_url"]),
            ("AICORE_AUTH_URL_US", profile["auth_url"]),
            ("AICORE_CLIENT_ID_US", profile["client_id"]),
            ("AICORE_CLIENT_SECRET_US", profile["client_secret"]),
            ("AICORE_RESOURCE_GROUP_US", profile["resource_group"]),
        ]
    else:  # JP
        profile = {
            "base_url": settings.aicore_base_url,
            "auth_url": settings.aicore_auth_url,
            "client_id": settings.aicore_client_id,
            "client_secret": settings.aicore_client_secret,
            "resource_group": settings.aicore_resource_group,
        }
        required_names = [
            ("AICORE_BASE_URL", profile["base_url"]),
            ("AICORE_AUTH_URL", profile["auth_url"]),
            ("AICORE_CLIENT_ID", profile["client_id"]),
            ("AICORE_CLIENT_SECRET", profile["client_secret"]),
            ("AICORE_RESOURCE_GROUP", profile["resource_group"]),
        ]

    missing = [name for name, value in required_names if not value]
    if missing:
        raise ValueError(
            "Missing required AI Core configuration values for"
            f" {instance} instance: " + ", ".join(missing)
        )

    return profile, instance

def _get_audio_proxy_client():
    """Return a singleton proxy client configured for the selected instance."""
    global _audio_proxy_client

    if _audio_proxy_client is not None:
        return _audio_proxy_client

    profile, instance = _resolve_audio_profile()

    logger.info(
        "Initializing audio transcription proxy client (%s region)", instance
    )
    _audio_proxy_client = get_proxy_client(
        proxy_version="gen-ai-hub",
        base_url=profile["base_url"],
        auth_url=profile["auth_url"],
        client_id=profile["client_id"],
        client_secret=profile["client_secret"],
        resource_group=profile["resource_group"],
    )
    return _audio_proxy_client

def _get_audio_model() -> GenerativeModel:
    """Return a singleton GenerativeModel for audio transcription."""
    global _audio_model

    if _audio_model is not None:
        return _audio_model

    proxy_client = _get_audio_proxy_client()
    logger.info(
        "Initializing audio transcription model: %s", settings.audio_transcription_model
    )
    _audio_model = GenerativeModel(
        proxy_client=proxy_client,
        model_name=settings.audio_transcription_model,
    )
    return _audio_model

async def transcribe_audio_bytes(
    audio_bytes: bytes,
    mime_type: str,
    prompt: str,
    enable_timestamps: bool = False,
) -> str:
    """Transcribe raw audio bytes and return the generated text."""

    if not audio_bytes:
        raise ValueError("Audio payload is empty")

    model = _get_audio_model()
    base64_data = base64.b64encode(audio_bytes).decode("utf-8")

    content = [
        {
            "role": "user",
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64_data,
                    }
                },
            ],
        }
    ]

    generation_config = {"audio_timestamp": True} if enable_timestamps else None

    loop = asyncio.get_running_loop()
    logger.debug(
        "Submitting audio transcription request (mime=%s, timestamps=%s)",
        mime_type,
        enable_timestamps,
    )

    def _invoke_model():
        return model.generate_content(
            content,
            generation_config=generation_config if generation_config else None,
        )

    response = await loop.run_in_executor(None, _invoke_model)

    text = getattr(response, "text", None)
    if not text:
        # Fallback to extracting text from candidates if necessary
        candidates = getattr(response, "candidates", None)
        if candidates:
            text = "\n".join(
                part.text
                for candidate in candidates
                for part in getattr(candidate, "content", [])
                if getattr(part, "text", None)
            ).strip()

    if not text:
        raise RuntimeError("Audio transcription response did not contain any text")

    logger.debug("Audio transcription completed (%d characters)", len(text))
    return text.strip()
                                                                            