import requests
import os

NAMESPACE = os.environ.get("NAMESPACE")
INTERNAL_API_URL = os.environ.get("INTERNAL_API_URL", f"http://internal-api.{NAMESPACE}:1111")


def scan_registry(config: dict[str, str], is_base_image: bool | None = None) -> list[dict[str, str]]:
    response = requests.post(f"{INTERNAL_API_URL}/registry/scan_registry", json=config)
    response.raise_for_status()
    registry_images = []
    for repo, tags in response.json().items():
        for tag, imgs in tags.items():
            for img in imgs:
                image = {
                    "image_id": img["image_id"],
                    "digest": img["digest"],
                    "repository": repo,
                    "tag": tag,
                    "layers": img["layers"],
                    "config": img["config"],
                    "registry_scan_config": config["id"],
                    "is_base_image": is_base_image,
                }
                registry_images.append(image)
    return registry_images


def get_repository_token(config: dict, repository: str) -> str:
    response = requests.post(
        f"{INTERNAL_API_URL}/registry/get_repository_token?repository={repository}",
        json=config,
    )
    response.raise_for_status()
    return response.text


def get_pull_url(config: dict) -> str:
    response = requests.post(f"{INTERNAL_API_URL}/registry/get_pull_url", json=config)
    response.raise_for_status()
    return response.text


def encrypt(s):
    return requests.get(f"{INTERNAL_API_URL}/key/encrypt/{s}").text


def decrypt(s):
    return requests.get(f"{INTERNAL_API_URL}/key/decrypt/{s}").text


def get_client_secret(client_id: str) -> str:
    params = {"client_id": client_id}
    return requests.get(f"{INTERNAL_API_URL}/auth0/get_client_secret", params=params).text
