import os
import httpx
import msgspec
from typing import List
from uuid import UUID
from app.domain.structs import RoomResponse, RoomCreate, JoinRoomRequest, MemberResponse

ROOMS_URL = os.getenv("ROOMS_SERVICE_URL", "http://127.0.0.1:8004")

async def create_room(client: httpx.AsyncClient, data: RoomCreate, raw_token: str) -> RoomResponse:
    url = f"{ROOMS_URL}/"
    headers = {"Authorization": f"Bearer {raw_token}", "Content-Type": "application/json"}
    content = msgspec.json.encode(data)
    
    response = await client.post(url, content=content, headers=headers)
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=RoomResponse)

async def get_all_rooms(client: httpx.AsyncClient, raw_token: str) -> List[RoomResponse]:
    url = f"{ROOMS_URL}/"
    headers = {"Authorization": f"Bearer {raw_token}"}
    
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=List[RoomResponse])

async def get_room(client: httpx.AsyncClient, room_id: UUID, raw_token: str) -> RoomResponse:
    url = f"{ROOMS_URL}/{room_id}"
    headers = {"Authorization": f"Bearer {raw_token}"}
    
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=RoomResponse)

async def end_room(client: httpx.AsyncClient, room_id: UUID, raw_token: str) -> RoomResponse:
    url = f"{ROOMS_URL}/{room_id}/end"
    headers = {"Authorization": f"Bearer {raw_token}"}
    
    response = await client.post(url, headers=headers)
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=RoomResponse)

async def join_room(client: httpx.AsyncClient, data: JoinRoomRequest, raw_token: str) -> MemberResponse:
    url = f"{ROOMS_URL}/join"
    headers = {"Authorization": f"Bearer {raw_token}", "Content-Type": "application/json"}
    content = msgspec.json.encode(data)
    
    response = await client.post(url, content=content, headers=headers)
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=MemberResponse)

async def leave_room(client: httpx.AsyncClient, room_id: UUID, raw_token: str) -> MemberResponse:
    url = f"{ROOMS_URL}/{room_id}/leave"
    headers = {"Authorization": f"Bearer {raw_token}"}
    
    response = await client.delete(url, headers=headers)
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=MemberResponse)