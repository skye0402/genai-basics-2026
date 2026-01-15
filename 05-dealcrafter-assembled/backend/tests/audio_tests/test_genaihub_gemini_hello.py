import os
import sys
from typing import Any, Callable
from dotenv import load_dotenv

load_dotenv()


def _install_requests_logger() -> None:
    import requests

    original_request: Callable[..., Any] = requests.sessions.Session.request

    def logged_request(self, method: str, url: str, **kwargs):  # type: ignore[no-untyped-def]
        print("\n=== gen_ai_hub outbound request ===")
        print(f"method: {method}")
        print(f"url: {url}")

        headers = kwargs.get("headers") or {}
        redacted_headers = dict(headers)
        if "Authorization" in redacted_headers:
            redacted_headers["Authorization"] = "***"
        print(f"headers: {redacted_headers}")

        params = kwargs.get("params")
        if params is not None:
            print(f"params: {params}")

        json_body = kwargs.get("json")
        if json_body is not None:
            print(f"json_keys: {list(json_body.keys()) if isinstance(json_body, dict) else type(json_body)}")

        data_body = kwargs.get("data")
        if data_body is not None:
            print(f"data_type: {type(data_body)}")

        return original_request(self, method, url, **kwargs)

    requests.sessions.Session.request = logged_request  # type: ignore[assignment]


def main() -> None:
    try:
        from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
        from gen_ai_hub.proxy.native.google_vertexai.clients import GenerativeModel
    except Exception as e:  # noqa: BLE001
        raise SystemExit(
            "gen_ai_hub is not installed in this backend venv.\n"
            "If you really want to run this debug script, install the archived SDK first:\n\n"
            "  uv add generative-ai-hub-sdk\n"
            "  uv sync\n\n"
            f"Import error: {type(e).__name__}: {e}"
        )

    _install_requests_logger()

    model_name = os.environ.get("AUDIO_MODEL_NAME", "gemini-2.5-flash").strip() or "gemini-2.5-flash"

    proxy_client = get_proxy_client("gen-ai-hub")
    model = GenerativeModel(proxy_client=proxy_client, model_name=model_name)

    content = [
        {
            "role": "user",
            "parts": [
                {
                    "text": "Hello world",
                }
            ],
        }
    ]

    resp = model.generate_content(content)
    print("\n=== model_response ===")
    print(resp)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"Unhandled error: {type(e).__name__}: {e}", file=sys.stderr)
        raise
