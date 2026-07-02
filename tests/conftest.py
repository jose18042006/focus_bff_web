import pytest
import httpx
from datetime import datetime, timedelta, timezone
from litestar.security.jwt import Token
from litestar.testing import TestClient
from litestar import Litestar

from app.main import app as bff_app
from app.core.security import SECRET_KEY

@pytest.fixture
def mock_http_client():
    return httpx.AsyncClient()

@pytest.fixture
def test_client():
    with TestClient(app=bff_app) as client:
        yield client

def create_mock_token(user_id: str, role: str = "student") -> str:
    token = Token(
        sub=user_id,
        exp=datetime.now(timezone.utc) + timedelta(hours=1),
        extras={"role": role},
    )
    return token.encode(secret=SECRET_KEY, algorithm="HS256")

