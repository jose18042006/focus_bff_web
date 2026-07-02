import pytest
from litestar.testing import TestClient
from app.main import app
from app.clients.base import get_http_client

def test_health_check_main():
    with TestClient(app=app) as client:
        response = client.get("/api/v1/status/health") 
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_http_client():
    client = await get_http_client()
    assert client is not None