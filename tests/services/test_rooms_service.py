import pytest
import httpx
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from litestar.exceptions import HTTPException

from app.services.rooms_service import proxy_get_room
from app.services.rooms_service import proxy_create_room, proxy_get_all_rooms, proxy_end_room, proxy_join_room, proxy_leave_room
from app.domain.structs import RoomCreate, JoinRoomRequest, MemberResponse, RoomResponse

@pytest.mark.asyncio
@patch("app.services.rooms_service.rooms_client.get_room")
async def test_proxy_get_room_success(mock_get_room):
    fake_room = RoomResponse(id=uuid4(), name="Test", capacity=5, creator_id=uuid4(), status="active", xp_multiplier=1.0, description=None)
    mock_get_room.return_value = fake_room
    
    client = AsyncMock()
    result = await proxy_get_room(client, fake_room.id, "token")
    
    assert result == fake_room
    mock_get_room.assert_called_once()

@pytest.mark.asyncio
@patch("app.services.rooms_service.rooms_client.get_room")
async def test_proxy_get_room_throws_503_when_offline(mock_get_room):
    mock_request = httpx.Request("GET", "url")
    mock_get_room.side_effect = httpx.RequestError("No connection", request=mock_request)
    
    client = AsyncMock()
    
    with pytest.raises(HTTPException) as exc:
        await proxy_get_room(client, uuid4(), "token")
    
    assert exc.value.status_code == 503
    assert "fuera de línea" in exc.value.detail

@pytest.mark.asyncio
@patch("app.services.rooms_service.rooms_client.create_room", new_callable=AsyncMock)
async def test_proxy_create_room(mock_create):
    fake_room = RoomResponse(id=uuid4(), name="T", capacity=5, creator_id=uuid4(), status="active", xp_multiplier=1.0, description=None)
    mock_create.return_value = fake_room
    res = await proxy_create_room(AsyncMock(), RoomCreate(name="T"), "tkn")
    assert res.name == "T"

@pytest.mark.asyncio
@patch("app.services.rooms_service.rooms_client.get_all_rooms", new_callable=AsyncMock)
async def test_proxy_get_all_rooms(mock_list):
    mock_list.return_value = []
    res = await proxy_get_all_rooms(AsyncMock(), "tkn")
    assert isinstance(res, list)

@pytest.mark.asyncio
@patch("app.services.rooms_service.rooms_client.end_room", new_callable=AsyncMock)
async def test_proxy_end_room(mock_end):
    fake_room = RoomResponse(id=uuid4(), name="T", capacity=5, creator_id=uuid4(), status="ended", xp_multiplier=1.0, description=None)
    mock_end.return_value = fake_room
    res = await proxy_end_room(AsyncMock(), uuid4(), "tkn")
    assert res.status == "ended"

@pytest.mark.asyncio
@patch("app.services.rooms_service.rooms_client.join_room", new_callable=AsyncMock)
async def test_proxy_join_room(mock_join):
    mock_join.return_value = MemberResponse(message="Ok", room_id=uuid4())
    res = await proxy_join_room(AsyncMock(), JoinRoomRequest(invitation_code="123"), "tkn")
    assert res.message == "Ok"

@pytest.mark.asyncio
@patch("app.services.rooms_service.rooms_client.leave_room", new_callable=AsyncMock)
async def test_proxy_leave_room_fails(mock_leave):
    mock_req = httpx.Request("DELETE", "")
    mock_leave.side_effect = httpx.HTTPStatusError("Error", request=mock_req, response=httpx.Response(400, request=mock_req, json={"detail": "Bad"}))
    with pytest.raises(HTTPException) as exc:
        await proxy_leave_room(AsyncMock(), uuid4(), "tkn")
    assert exc.value.status_code == 400