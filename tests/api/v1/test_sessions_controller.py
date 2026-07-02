import pytest
from unittest.mock import patch, PropertyMock, AsyncMock
from uuid import uuid4
from app.domain.structs import SessionReportResponse
from tests.conftest import create_mock_token

@patch("app.api.v1.session_controller.orchestrate_session_reports", new_callable=AsyncMock)
@patch("litestar.connection.Request.user", new_callable=PropertyMock)
def test_get_reports_controller(mock_user, mock_orchestrate, test_client):
    user_id = str(uuid4())
    mock_user.return_value = {"sub": user_id, "role": "dm"}
    
    mock_orchestrate.return_value = SessionReportResponse(reports=[], total_count=0)
    
    token = create_mock_token(user_id=user_id, role="dm")

    response = test_client.get(
        "/api/v1/sessions/reports?limit=15&sort_order=asc",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    mock_orchestrate.assert_called_once()
    
    called_filters = mock_orchestrate.call_args.kwargs["filters"]
    assert called_filters.limit == 15
    assert called_filters.sort_order == "asc"