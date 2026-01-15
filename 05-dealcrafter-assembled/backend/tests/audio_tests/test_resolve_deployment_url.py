import os
from dotenv import load_dotenv

from ai_core_sdk.ai_core_v2_client import AICoreV2Client
from ai_core_sdk.models import Deployment

load_dotenv()

def main() -> None:
    audio_model_name = os.environ.get("AUDIO_MODEL_NAME", "").strip()
    if not audio_model_name:
        raise SystemExit("Missing AUDIO_MODEL_NAME in environment/.env")

    client = AICoreV2Client.from_env()
    deployments = client.deployment.query(scenario_id='foundation-models')
    for deployment in deployments.resources:
        deployment: Deployment
        if deployment.details.get("resources").get("backend_details").get("model").get("name") == audio_model_name:
            deployment_url = deployment.deployment_url
            break

    print(f"audio_model_name: {audio_model_name}")
    print(f"deployment_url: {deployment_url}")

    token = client.rest_client.get_token()
    print(f"token_has_bearer_prefix: {token.startswith('Bearer ')}")
    print(f"resource_group_header: {client.rest_client.headers.get('AI-Resource-Group')}")


if __name__ == "__main__":
    main()
