"""Audio transcription service via SAP AI Core deployment (sap-ai-sdk-core + direct HTTP call)."""
from __future__ import annotations

import asyncio
import base64
import logging
from typing import Optional

import httpx
from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from ai_core_sdk.models import Deployment

from app.core.config import settings

logger = logging.getLogger(__name__)

_aicore_client: Optional[AICoreV2Client] = None
_audio_deployment_url: Optional[str] = None


def _get_aicore_client() -> AICoreV2Client:
    global _aicore_client

    if _aicore_client is not None:
        return _aicore_client

    _aicore_client = AICoreV2Client.from_env()
    return _aicore_client


def _get_audio_deployment_url() -> str:
    client = _get_aicore_client()

    global _audio_deployment_url
    if _audio_deployment_url:
        return _audio_deployment_url

    audio_model_name = (settings.audio_model_name or "").strip()
    if not audio_model_name:
        raise ValueError("AUDIO_MODEL_NAME must be configured")

    deployments = client.deployment.query(scenario_id="foundation-models")
    for deployment in deployments.resources:
        deployment = deployment  # type: Deployment
        model_name = (
            deployment.details.get("resources", {})
            .get("backend_details", {})
            .get("model", {})
            .get("name")
        )
        if model_name == audio_model_name:
            _audio_deployment_url = str(deployment.deployment_url).rstrip("/")
            return _audio_deployment_url

    raise RuntimeError(f"Could not find deployment for AUDIO_MODEL_NAME='{audio_model_name}'")

async def transcribe_audio_bytes(
    audio_bytes: bytes,
    mime_type: str,
    prompt: str,
    enable_timestamps: bool = False,
) -> str:
    """Transcribe raw audio bytes and return the generated text."""

    if not audio_bytes:
        raise ValueError("Audio payload is empty")

    deployment_url = _get_audio_deployment_url()
    model_name = (settings.audio_model_name or "").strip()
    if not model_name:
        raise ValueError("AUDIO_MODEL_NAME must be configured for Gemini multimodal transcription")

    endpoint = f"{deployment_url}/models/{model_name}:generateContent"

    client = _get_aicore_client()

    headers: dict[str, str] = {
        "Authorization": client.rest_client.get_token(),
    }
    resource_group = client.rest_client.headers.get("AI-Resource-Group")
    if resource_group:
        headers["AI-Resource-Group"] = resource_group

    params: dict[str, str] = {
        "$alt": "json;enum-encoding=int",
    }

    headers.setdefault(
        "x-goog-request-params",
        f"model=projects/not-applicable/locations/not-applicable/publishers/google/models/{model_name}",
    )

    loop = asyncio.get_running_loop()
    logger.debug(
        "Submitting audio transcription request (mime=%s, timestamps=%s)",
        mime_type,
        enable_timestamps,
    )

    def _invoke_sync() -> str:
        base64_data = base64.b64encode(audio_bytes).decode("utf-8")

        body: dict[str, object] = {
            "contents": [
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
            ],
        }
        if enable_timestamps:
            body["generationConfig"] = {"audioTimestamp": True}

        with httpx.Client(timeout=120) as http:
            resp = http.post(endpoint, params=params, headers=headers, json=body)
            resp.raise_for_status()
            payload = resp.json()

        if not isinstance(payload, dict):
            raise RuntimeError("Audio transcription response was not JSON object")

        candidates = payload.get("candidates")
        if isinstance(candidates, list) and candidates:
            parts = (
                candidates[0]
                .get("content", {})
                .get("parts", [])
            )
            if isinstance(parts, list):
                text = "\n".join(
                    part.get("text", "")
                    for part in parts
                    if isinstance(part, dict) and part.get("text")
                ).strip()
                if text:
                    return text

        raise RuntimeError("Audio transcription response did not contain any text")

    text = await loop.run_in_executor(None, _invoke_sync)
    logger.debug("Audio transcription completed (%d characters)", len(text))
    return text
                                                                            