import pytest
import httpx
import msgspec
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
from app.clients.stats_client import process_batch_sessions
from app.domain.structs import SyncPayload, SessionItem, SyncSessionResponse,ReportFilters, SessionReportResponse
from app.clients.stats_client import fetch_session_reports

@pytest.mark.asyncio
@patch.object(httpx.AsyncClient, "post")
async def test_process_batch_sessions_client(mock_post, mock_http_client):
    mock_response_struct = SyncSessionResponse(total_exp_gained=150, time_trials_completed=1)
    mock_response_bytes = msgspec.json.encode(mock_response_struct)
    
    mock_post.return_value = httpx.Response(
        status_code=200, 
        content=mock_response_bytes, 
        request=httpx.Request("POST", "http://test.com")
    )
    
    payload = SyncPayload(
        sessions=[
            SessionItem(
                activity_type="pomodoro",
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc)
            )
        ]
    )
    
    result = await process_batch_sessions(
        client=mock_http_client,
        payload=payload,
        raw_token="fake_jwt_token"
    )
    assert result.total_exp_gained == 150

@pytest.mark.asyncio
@patch.object(httpx.AsyncClient, "get")
async def test_fetch_session_reports_client(mock_get, mock_http_client):
    mock_struct = SessionReportResponse(reports=[], total_count=0)
    mock_response = httpx.Response(200, content=msgspec.json.encode(mock_struct),request=httpx.Request("POST", "http://test.com"))
    mock_get.return_value = mock_response

    filters = ReportFilters(limit=10, sort_order="asc")
    
    await fetch_session_reports(mock_http_client, filters, "token")
    
    mock_get.assert_called_once()
    called_params = mock_get.call_args.kwargs["params"]
    
    assert "limit" in called_params
    assert called_params["limit"] == 10
    assert "user_id" not in called_params