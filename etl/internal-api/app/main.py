from fastapi import FastAPI
from .routers import key, auth0, registry
import logging

logging.basicConfig(format="%(asctime)s | %(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger("internal-api")


app = FastAPI()

app.include_router(key.router)
app.include_router(auth0.router)
app.include_router(registry.router)
