import pytest
import httpx
from uuid import uuid4
from unittest.mock import patch, AsyncMock
from litestar.exceptions import HTTPException
from app.services.auth_service import orchestrate_login
from app.domain.structs import LoginPayload, TokenResponse, RegisterPayload, RegisterResponse
from app.services.auth_service import orchestrate_register

@pytest.mark.asyncio
@patch("app.services.auth_service.proxy_login", new_callable=AsyncMock)
async def test_orchestrate_login_success(mock_proxy, mock_http_client):
    mock_proxy.return_value = TokenResponse(access_token="abc", token_type="bearer")
    payload = LoginPayload(email="t@t.com", password="123")
    
    result = await orchestrate_login(mock_http_client, payload)
    assert result.access_token == "abc"

@pytest.mark.asyncio
@patch("app.services.auth_service.proxy_login", new_callable=AsyncMock)
async def test_orchestrate_login_fails(mock_proxy, mock_http_client):
    mock_response = httpx.Response(401, request=httpx.Request("POST", ""))
    mock_proxy.side_effect = httpx.HTTPStatusError("Error", request=mock_response.request, response=mock_response)
    
    payload = LoginPayload(email="t@t.com", password="123")
    
    with pytest.raises(HTTPException) as exc:
        await orchestrate_login(mock_http_client, payload)
        
    assert exc.value.status_code == 401
    assert "Credenciales" in exc.value.detail

@pytest.mark.asyncio
@patch("app.services.auth_service.proxy_register", new_callable=AsyncMock)
async def test_orchestrate_register_success(mock_proxy, mock_http_client):
    user_id = uuid4()
    mock_proxy.return_value = RegisterResponse(message="Created", id=user_id, email="fury@dev.com")
    
    payload = RegisterPayload(email="fury@dev.com", password="secure_password")
    result = await orchestrate_register(mock_http_client, payload)
    
    assert result.message == "Created"
    assert result.id == user_id
    mock_proxy.assert_called_once_with(client=mock_http_client, payload=payload)

@pytest.mark.asyncio
@patch("app.services.auth_service.proxy_register", new_callable=AsyncMock)
async def test_orchestrate_register_fails(mock_proxy, mock_http_client):
    mock_req = httpx.Request("POST", "")
    mock_proxy.side_effect = httpx.HTTPStatusError("Error", request=mock_req, response=httpx.Response(400, request=mock_req))
    with pytest.raises(HTTPException):
        await orchestrate_register(mock_http_client, RegisterPayload(email="t@t.com", password="123"))