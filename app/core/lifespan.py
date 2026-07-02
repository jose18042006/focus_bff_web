from contextlib import asynccontextmanager
import httpx
from litestar import Litestar

@asynccontextmanager
async def http_client_lifespan(app: Litestar):

    async with httpx.AsyncClient(timeout=10.0) as client:
        app.state.http_client = client
        yield