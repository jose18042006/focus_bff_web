from uuid import uuid4
import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from app.domain.structs import UserStatsResponse
from tests.conftest import create_mock_token

@patch("app.api.v1.users_controller.orchestrate_get_my_stats", new_callable=AsyncMock)
def test_get_my_stats_controller_success(mock_orchestrate, test_client):
    mock_orchestrate.return_value = UserStatsResponse(
        total_exp=500, current_level=4
    )
    test_uuid = str(uuid4())
    valid_token = create_mock_token(test_uuid)

    headers = {"Authorization": f"Bearer {valid_token}"}
    response = test_client.get("/api/v1/users/me/stats", headers=headers)
    
    assert response.status_code == 200 
    assert response.json()["total_exp"] == 500
    assert response.json()["current_level"] == 4
    mock_orchestrate.assert_called_once()

@patch("app.api.v1.users_controller.orchestrate_get_my_stats", new_callable=AsyncMock)
def test_get_my_stats_controller_unauthorized(mock_orchestrate, test_client):
    response = test_client.get("/api/v1/users/me/stats")
    
    assert response.status_code == 401
    
    mock_orchestrate.assert_not_called()