import pytest
import httpx
from uuid import uuid4
from unittest.mock import patch, AsyncMock
from litestar.exceptions import PermissionDeniedException
from app.services.report_service import orchestrate_session_reports
from app.domain.structs import ReportFilters, SessionReportResponse
from unittest.mock import MagicMock
from litestar.exceptions import HTTPException

@pytest.mark.asyncio
async def test_student_cannot_spy_others(mock_http_client):
    logged_user = uuid4()
    other_user = uuid4()
    filters = ReportFilters(user_id=other_user)     
    
    with pytest.raises(PermissionDeniedException) as exc:
        await orchestrate_session_reports(
            mock_http_client, filters, "token", logged_user, "student"
        )
    assert "otro usuario" in exc.value.detail

@pytest.mark.asyncio
async def test_student_cannot_view_room_reports(mock_http_client):
    filters = ReportFilters(room_id=uuid4())
    
    with pytest.raises(PermissionDeniedException) as exc:
        await orchestrate_session_reports(
            mock_http_client, filters, "token", uuid4(), "student"
        )
    assert "salas enteras" in exc.value.detail

@pytest.mark.asyncio
@patch("app.services.report_service.get_room")
async def test_dm_cannot_view_others_rooms(mock_get_room, mock_http_client):
    dm_id = uuid4()
    filters = ReportFilters(room_id=uuid4())

    mock_room_response = MagicMock()
    mock_room_response.creator_id = uuid4() 
    mock_get_room.return_value = mock_room_response

    with pytest.raises(PermissionDeniedException) as exc:
        await orchestrate_session_reports(
            mock_http_client, filters, "token", dm_id, "dm"
        )

@pytest.mark.asyncio
@patch("app.services.report_service.get_room")
@patch("app.services.report_service.fetch_session_reports", new_callable=AsyncMock)
async def test_dm_success_room_fetch(mock_fetch, mock_get_room, mock_http_client):
    dm_id = uuid4()
    filters = ReportFilters(room_id=uuid4())

    mock_room_response = MagicMock()
    mock_room_response.creator_id = dm_id 
    mock_get_room.return_value = mock_room_response
    
    mock_fetch.return_value = SessionReportResponse(reports=[], total_count=0)

    result = await orchestrate_session_reports(
        mock_http_client, filters, "token", dm_id, "dm"
    )

@pytest.mark.asyncio
@patch("app.services.report_service.get_room")
async def test_dm_room_not_found(mock_get_room, mock_http_client):
    mock_req = httpx.Request("GET", "")
    mock_get_room.side_effect = httpx.HTTPStatusError("Not Found", request=mock_req, response=httpx.Response(404, request=mock_req))
    
    with pytest.raises(HTTPException) as exc:
        await orchestrate_session_reports(mock_http_client, ReportFilters(room_id=uuid4()), "token", uuid4(), "dm")
    assert exc.value.status_code == 404

@pytest.mark.asyncio
@patch("app.services.report_service.fetch_session_reports", new_callable=AsyncMock)
async def test_fetch_reports_fails(mock_fetch, mock_http_client):
    mock_req = httpx.Request("GET", "")
    mock_fetch.side_effect = httpx.HTTPStatusError("Error", request=mock_req, response=httpx.Response(500, request=mock_req))
    
    with pytest.raises(HTTPException) as exc:
        await orchestrate_session_reports(mock_http_client, ReportFilters(), "token", uuid4(), "student")
    assert exc.value.status_code == 500