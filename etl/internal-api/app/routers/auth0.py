from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
import os
import httpx
import logging

logger = logging.getLogger("internal-api.auth0")


class Auth0:
    AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")

    async def __aenter__(self):
        transport = httpx.AsyncHTTPTransport(retries=2)
        self.client = httpx.AsyncClient(base_url=f"https://{self.AUTH0_DOMAIN}", transport=transport)
        token = await self.get_token()
        self.client.headers = {"Authorization": f"Bearer {token}"}
        return self

    async def __aexit__(self, *err):
        await self.client.aclose()
        self.client = None

    async def get_token(self) -> str:
        payload = {
            "client_id": self.AUTH0_CLIENT_ID,
            "client_secret": self.AUTH0_CLIENT_SECRET,
            "audience": f"https://{self.AUTH0_DOMAIN}/api/v2/",
            "grant_type": "client_credentials",
        }
        response = await self.client.post("/oauth/token", json=payload)
        response.raise_for_status()
        result = response.json()
        return result["access_token"]

    async def get_client_secret(self, client_id: str) -> str:
        response = await self.client.get(f"/api/v2/clients/{client_id}")
        response.raise_for_status()
        result = response.json()
        return result["client_secret"]


router = APIRouter()


@router.get("/auth0/get_client_secret", tags=["auth0"], response_class=PlainTextResponse)
async def get_client_secret(client_id: str):
    async with Auth0() as auth0:
        return await auth0.get_client_secret(client_id)
