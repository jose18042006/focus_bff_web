import pytest
import httpx
import msgspec
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime
from app.clients.rooms_client import get_room
from app.domain.structs import RoomResponse
from app.clients.rooms_client import create_room, get_all_rooms, join_room, leave_room, end_room
from app.domain.structs import RoomCreate, JoinRoomRequest, MemberResponse
from typing import List

@pytest.mark.asyncio
async def test_get_room_success():
    
    fake_room_id = uuid4()
    fake_room = RoomResponse(
        id=fake_room_id, name="Sala de Estudio", capacity=5, 
        creator_id=uuid4(), status="active", xp_multiplier=1.5, description=None
    )
    
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    
    mock_response = MagicMock() 
    mock_response.raise_for_status.return_value = None
    mock_response.content = msgspec.json.encode(fake_room)
    
    mock_client.get.return_value = mock_response

    result = await get_room(mock_client, fake_room_id, "token_falso")

    assert result.id == fake_room_id
    assert result.name == "Sala de Estudio"
    assert result.xp_multiplier == 1.5
    mock_client.get.assert_called_once()

@pytest.mark.asyncio
async def test_create_room_success():
    fake_room = RoomResponse(id=uuid4(), name="Nueva Sala", capacity=5, creator_id=uuid4(), status="active", xp_multiplier=1.0, description=None)
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock() 
    mock_response.raise_for_status.return_value = None
    mock_response.content = msgspec.json.encode(fake_room)
    mock_client.post.return_value = mock_response

    data = RoomCreate(name="Nueva Sala", capacity=5, xp_multiplier=1.0)
    result = await create_room(mock_client, data, "token")

    assert result.name == "Nueva Sala"
    mock_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_rooms_success():
    fake_room = RoomResponse(id=uuid4(), name="Sala", capacity=5, creator_id=uuid4(), status="active", xp_multiplier=1.0, description=None)
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock() 
    mock_response.raise_for_status.return_value = None
    mock_response.content = msgspec.json.encode([fake_room])
    mock_client.get.return_value = mock_response

    result = await get_all_rooms(mock_client, "token")

    assert len(result) == 1
    assert result[0].name == "Sala"

@pytest.mark.asyncio
async def test_join_room_success():
    fake_member = MemberResponse(message="Te uniste", room_id=uuid4())
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock() 
    mock_response.raise_for_status.return_value = None
    mock_response.content = msgspec.json.encode(fake_member)
    mock_client.post.return_value = mock_response

    result = await join_room(mock_client, JoinRoomRequest(invitation_code="ABCDEF"), "token")

    assert result.message == "Te uniste"

@pytest.mark.asyncio
async def test_end_room_client():
    fake_room = RoomResponse(id=uuid4(), name="Test", capacity=5, creator_id=uuid4(), status="ended", xp_multiplier=1.0, description=None)
    mock_client = AsyncMock()
    mock_res = MagicMock()
    mock_res.raise_for_status.return_value = None
    mock_res.content = msgspec.json.encode(fake_room)
    mock_client.post.return_value = mock_res

    res = await end_room(mock_client, uuid4(), "token")
    assert res.status == "ended"

@pytest.mark.asyncio
async def test_leave_room_client():
    fake_member = MemberResponse(message="Adios", room_id=uuid4())
    mock_client = AsyncMock()
    mock_res = MagicMock()
    mock_res.raise_for_status.return_value = None
    mock_res.content = msgspec.json.encode(fake_member)
    mock_client.delete.return_value = mock_res

    res = await leave_room(mock_client, uuid4(), "token")
    assert res.message == "Adios"