import os
from typing import Any

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from ai_core_sdk.models import Deployment

import httpx
from dotenv import load_dotenv

load_dotenv()


def _resolve_deployment_url_by_model_name(client: AICoreV2Client, model_name: str) -> str:
    deployments = client.deployment.query(scenario_id="foundation-models")
    for deployment in deployments.resources:
        deployment = deployment  # type: Deployment
        deployed_name = (
            deployment.details.get("resources", {})
            .get("backend_details", {})
            .get("model", {})
            .get("name")
        )
        if deployed_name == model_name:
            return str(deployment.deployment_url).rstrip("/")

    raise RuntimeError(f"Could not find deployment for AUDIO_MODEL_NAME='{model_name}'")


def _build_headers(client: AICoreV2Client) -> dict[str, str]:
    headers: dict[str, str] = {
        "Authorization": client.rest_client.get_token(),
    }
    resource_group = client.rest_client.headers.get("AI-Resource-Group")
    if resource_group:
        headers["AI-Resource-Group"] = resource_group
    return headers


def _try_post_json(http: httpx.Client, url: str, headers: dict[str, str], params: dict[str, str], body: dict[str, Any]):
    print(f"\n=== POST {url}")
    try:
        resp = http.post(url, headers=headers, params=params, json=body)
        print(f"status: {resp.status_code}")
        content_type = resp.headers.get("content-type", "")
        print(f"content-type: {content_type}")
        text = resp.text
        print(f"body (first 800 chars): {text[:800]}")
    except Exception as e:
        print(f"request_error: {type(e).__name__}: {e}")


def main() -> None:
    model_name = os.environ.get("AUDIO_MODEL_NAME", "").strip()
    if not model_name:
        raise SystemExit("Missing AUDIO_MODEL_NAME in environment/.env")

    client = AICoreV2Client.from_env()
    deployment_url = _resolve_deployment_url_by_model_name(client, model_name)

    print(f"model_name: {model_name}")
    print(f"deployment_url: {deployment_url}")

    endpoint = f"{deployment_url}/models/{model_name}:generateContent"

    headers = _build_headers(client)

    # GenAI Hub uses this query param for the Gemini generateContent call.
    params = {
        "$alt": "json;enum-encoding=int",
    }

    # Vertex-style request body (matches gen_ai_hub native google_vertexai client)
    body: dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": "Hello world",
                    }
                ],
            }
        ]
    }

    with httpx.Client(timeout=60) as http:
        _try_post_json(
            http=http,
            url=endpoint,
            headers=headers,
            params=params,
            body=body,
        )


if __name__ == "__main__":
    main()
