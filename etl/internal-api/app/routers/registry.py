from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
import json
import httpx
import aiometer
import asyncio
import functools
import time
from collections import ChainMap
from pydantic import BaseModel
from urllib.parse import urlparse
import logging

logger = logging.getLogger("internal-api.registry")


class ReposFilter(BaseModel):
    repositories: list[str] | None = None
    architectures: list[str] | None = None
    oss: list[str] | None = None


class RegistryConfig(BaseModel):
    provider: str
    registry_url: str
    username: str | None = None
    password: str | None = None
    token: str | None = None
    repos_filter: ReposFilter | None = ReposFilter()


class ContainerRegistry:
    def __init__(self, params: RegistryConfig) -> None:
        self.params = params
        self.auth_base = None
        self.auth_service = None

    async def __aenter__(self):
        transport = httpx.AsyncHTTPTransport(retries=2)
        limits = httpx.Limits(max_keepalive_connections=15, max_connections=40)
        self.client = httpx.AsyncClient(follow_redirects=True, transport=transport, limits=limits)
        await self._auto_detect_auth_params()
        return self

    async def __aexit__(self, *err):
        await self.client.aclose()
        self.client = None

    async def _auto_detect_auth_params(self):
        url = f"{self.params.registry_url}/v2/"
        max_retries = 3
        while True:
            try:
                response = await self.client.get(url)
                break
            except httpx.ConnectError as e:
                if max_retries > 0:
                    logger.warn(e)
                    max_retries -= 1
                    await asyncio.sleep(0.01)
                else:
                    raise e
        parts = response.headers["www-authenticate"].removeprefix("Bearer ").split(",")
        params = {p.split("=")[0]: p.split("=")[1] for p in parts}
        self.auth_base = params["realm"][1:-1]
        self.auth_service = params["service"][1:-1]

    async def get_pull_url(self):
        url = urlparse(self.params.registry_url)
        return f"{url.netloc}/{url.path.split('/')[-1]}".rstrip("/")

    async def get_repository_token(self, repository: str = None) -> str:
        if self.params.token:
            return self.params.token
        params = {
            "service": self.auth_service,
            "scope": f"repository:{repository}:pull" if repository else "registry:catalog:*",
        }
        response = await self.client.get(
            url=self.auth_base,
            auth=(self.params.username, self.params.password),
            params=params,
        )
        response.raise_for_status()
        data = response.json()
        token = data["token"]
        return token

    async def _fetch_from_registry(
        self, repository: str, endpoint: str, token: str = None, accepts: list[str] = []
    ) -> dict:
        if token is None:
            token = await self.get_repository_token(repository)
        # headers.append(("Authorization", f"Bearer {token}"))
        headers = [("Authorization", f"Bearer {token}")]
        for x in accepts:
            headers.append(("Accept", x))
        url = f"{self.params.registry_url}/v2/{repository}/{endpoint}"
        max_retries = 3
        while True:
            try:
                response = await self.client.get(url, headers=headers)
                response.raise_for_status()
                break
            except httpx.ConnectError as e:
                if max_retries > 0:
                    logger.warn(e)
                    max_retries -= 1
                    await asyncio.sleep(0.01)
                else:
                    raise e

        return response

    async def varify_registry_login(self) -> bool:
        try:
            await self.get_repository_token()
            return True
        except Exception as e:
            if e.args[0] == "auth_error":
                return False
            raise e

    def _is_selected_platform(self, architecture: str, os: str = None) -> bool:
        return not (
            (self.params.repos_filter.architectures and architecture not in self.params.repos_filter.architectures)
            or (os and self.params.repos_filter.oss and os not in self.params.repos_filter.oss)
        )

    async def get_image(self, repository: str, digest: str, version: int, token: str) -> dict:
        accepts = [
            "application/vnd.docker.distribution.manifest.v2+json",
            "application/vnd.oci.image.manifest.v1+json",
        ]
        response = await self._fetch_from_registry(repository, f"manifests/{digest}", token=token, accepts=accepts)

        # V1 image format (pre Docker v1.10) is deprecated and not supported
        if response.headers["content-type"] not in accepts:
            img = f"{repository}/{digest}"
            logger.warn(f'Skipping image "{img}" due to unsupported V1 manifest format')
            return

        image = {}
        data = response.json()
        config_digest = data["config"]["digest"]
        image["schema_version"] = version
        image["digest"] = digest if version == 2 else response.headers.get("docker-content-digest")
        image["layers"] = [layer["digest"] for layer in data["layers"]]
        image["image_id"] = config_digest
        response = await self._fetch_from_registry(repository, f"blobs/{image['image_id']}", token=token)
        data = response.json()
        data.pop("container_config", None)
        image["config"] = data

        if not self._is_selected_platform(data["architecture"], data["os"]):
            platform = f'{data["architecture"]}/{data["os"]}'
            logger.info(f'Skipping image "{repository}/{config_digest}" due to filtered out platform "{platform}"')
            image = None

        return image

    # async def list_images(self, repository: str, tag: str, token: str) -> list:
    async def list_images(self, repository: str, tag: str) -> list:
        logger.info(f'Fetching "{repository}/{tag}"')

        accepts = [
            "application/vnd.docker.distribution.manifest.list.v2+json",
            "application/vnd.oci.image.index.v1+json",
        ]
        response = await self._fetch_from_registry(repository, f"manifests/{tag}", accepts=accepts)

        token = response.request.headers["Authorization"].removeprefix("Bearer ")

        data = response.json()
        images = []
        if data["schemaVersion"] == 2:
            for m in data["manifests"]:
                if self._is_selected_platform(m["platform"]["architecture"], m["platform"]["os"]):
                    image = await self.get_image(repository, m["digest"], 2, token)
                    if image:
                        images.append(image)
        else:
            if self._is_selected_platform(data["architecture"]):
                image = await self.get_image(repository, tag, 1, token)
                if image:
                    images.append(image)

        return tag, images

    async def list_tags(self, repository) -> list:
        tags = {}
        try:
            response = await self._fetch_from_registry(repository, "tags/list")
            # req_headers = response.request.headers["Authorization"]
            # token = req_headers.removeprefix("Bearer ")
            data = response.json()
            jobs = []
            for tag in data["tags"]:
                # task = functools.partial(self.list_images, repository, tag, token)
                task = functools.partial(self.list_images, repository, tag)
                jobs.append(task)
            results = await aiometer.run_all(jobs, max_at_once=20)
            tags = {tag: images for tag, images in results if images}
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise e
            else:
                logger.warn(e)
        return {repository: tags}

    async def list_repository_names(self) -> list:
        url = f"{self.params.registry_url}/v2/_catalog"
        token = await self.get_repository_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["repositories"]

    async def scan_registry(self) -> dict:
        if not self.params.repos_filter.repositories:
            self.params.repos_filter.repositories = await self.list_repository_names()
        tasks = []
        for repository in self.params.repos_filter.repositories:
            tasks.append(self.list_tags(repository))
        results = await asyncio.gather(*tasks)
        return dict(ChainMap(*results))


class DockerHub(ContainerRegistry):
    def __init__(self, params: RegistryConfig) -> None:
        self.hub_base = "https://hub.docker.com"
        self.namespace = params.registry_url
        params.registry_url = "https://registry-1.docker.io"
        super().__init__(params)

    async def get_hub_token(self) -> str:
        token = None
        try:
            auth = {"username": self.params.username, "password": self.params.password}
            url = f"{self.hub_base}/v2/users/login"
            response = await self.client.post(url, json=auth)
            response.raise_for_status()
            data = response.json()
            token = data["token"]
        except Exception as e:
            if type(e).__name__ == "HTTPError" and e.response.status_code == 401:
                logger.error(e.response.json()["detail"])
                raise Exception("auth_error")
            else:
                raise e
        return token

    async def _fetch_from_hub(self, url: str) -> list:
        token = await self.get_hub_token()
        headers = {"Authorization": f"Bearer {token}"}
        results = []
        while url:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            results += data["results"]
            url = data["next"]
        return results

    async def varify_hub_login(self) -> bool:
        try:
            await self.get_hub_token()
            return True
        except Exception as e:
            if e.args[0] == "auth_error":
                return False
            raise e

    async def list_repository_names(self) -> list:
        url = f"{self.hub_base}/v2/namespaces/{self.namespace}/repositories?page_size=100"
        repositories = await self._fetch_from_hub(url)
        return [self.namespace + "/" + r["name"] for r in repositories]


class Artifactory(ContainerRegistry):
    def __init__(self, params: RegistryConfig) -> None:
        super().__init__(params)


PROVIDERS = {"dockerhub": DockerHub, "artifactory": Artifactory}


def registry_factory(registry_params: RegistryConfig) -> ContainerRegistry:
    try:
        return PROVIDERS[registry_params.provider](registry_params)
    except KeyError:
        logger.error(f'Unknown provider "{registry_params.provider}"')


router = APIRouter()


@router.post("/registry/scan_registry", tags=["registry"])
async def scan_registry(config: RegistryConfig):
    async with registry_factory(config) as registry:
        return await registry.scan_registry()


@router.post(
    "/registry/get_repository_token",
    tags=["registry"],
    response_class=PlainTextResponse,
)
async def get_repository_token(config: RegistryConfig, repository: str):
    async with registry_factory(config) as registry:
        return await registry.get_repository_token(repository)


@router.post("/registry/get_pull_url", tags=["registry"], response_class=PlainTextResponse)
async def get_pull_url(config: RegistryConfig):
    async with registry_factory(config) as registry:
        return await registry.get_pull_url()
