import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone
from tests.conftest import create_mock_token
from app.domain.structs import SyncResponse


@patch("app.api.v1.sync_controller.orchestrate_sync", new_callable=AsyncMock)
def test_sync_controller_success(mock_orchestrate, test_client):

    mock_orchestrate.return_value = SyncResponse(
        status="synchronized",
        processed_sessions_count=1,
        total_exp=100,
        total_exp_gained=50,
        current_level=2,
        leveled_up=True,
        levels_gained=1,
        rewards=[]
    )
    token = create_mock_token(user_id=str(uuid4()))
    payload = {
        "sessions": [
            {
                "activity_type": "focus",
                "start_time": datetime.now(timezone.utc).isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat()
            }
        ]
    }
    response = test_client.post(
        "/api/v1/sync",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201  
    data = response.json()
    assert data["status"] == "synchronized"
    assert data["total_exp"] == 100

    mock_orchestrate.assert_called_once()
    assert mock_orchestrate.call_args.kwargs["raw_token"] == token

    