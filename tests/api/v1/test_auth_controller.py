import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from app.domain.structs import RegisterResponse, TokenResponse


@patch("app.api.v1.auth_controller.orchestrate_register", new_callable=AsyncMock)
def test_register_controller(mock_orchestrate, test_client):
    mock_orchestrate.return_value = RegisterResponse(
        message="Created", id=uuid4(), email="test@test.com"
    )
    
    payload = {"email": "test@test.com", "password": "123", "role": "student"}
    response = test_client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 201
    assert response.json()["email"] == "test@test.com"
    mock_orchestrate.assert_called_once()

@patch("app.api.v1.auth_controller.orchestrate_login", new_callable=AsyncMock)
def test_login_controller(mock_orchestrate, test_client):
    mock_orchestrate.return_value = TokenResponse(
        access_token="fake_token_123", token_type="bearer"
    )
    
    payload = {"email": "test@test.com", "password": "123"}
    response = test_client.post("/api/v1/auth/login", json=payload)
    
    assert response.status_code == 201 
    assert response.json()["access_token"] == "fake_token_123"