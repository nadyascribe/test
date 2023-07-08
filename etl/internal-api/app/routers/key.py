from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
import os
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger("internal-api.key")


scribe_key = Fernet(os.environ.get("SCRIBE_ALMIGHTY_FERNET_KEY").encode())

router = APIRouter()


@router.get("/key/encrypt/{key}", tags=["key"], response_class=PlainTextResponse)
async def encrypt(key: str):
    return scribe_key.encrypt(key.encode()) if key else key


@router.get("/key/decrypt/{key}", tags=["key"], response_class=PlainTextResponse)
async def decrypt(key: str):
    return scribe_key.decrypt(key.encode()) if key else key
