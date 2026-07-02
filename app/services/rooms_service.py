import httpx
from uuid import UUID
from typing import List

from app.clients import rooms_client
from app.domain.structs import RoomResponse, RoomCreate, JoinRoomRequest, MemberResponse
from app.core.exceptions import handle_httpx_error

async def proxy_create_room(http_client: httpx.AsyncClient, data: RoomCreate, raw_token: str) -> RoomResponse:
    try:
        return await rooms_client.create_room(http_client, data, raw_token)
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error al intentar crear la sala.")

async def proxy_get_all_rooms(http_client: httpx.AsyncClient, raw_token: str) -> List[RoomResponse]:
    try:
        return await rooms_client.get_all_rooms(http_client, raw_token)
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error al obtener la lista de salas activas.")

async def proxy_get_room(http_client: httpx.AsyncClient, room_id: UUID, raw_token: str) -> RoomResponse:
    try:
        return await rooms_client.get_room(http_client, room_id, raw_token)
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error al consultar los detalles de la sala.")

async def proxy_end_room(http_client: httpx.AsyncClient, room_id: UUID, raw_token: str) -> RoomResponse:
    try:
        return await rooms_client.end_room(http_client, room_id, raw_token)
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error al intentar cerrar la sala.")

async def proxy_join_room(http_client: httpx.AsyncClient, data: JoinRoomRequest, raw_token: str) -> MemberResponse:
    try:
        return await rooms_client.join_room(http_client, data, raw_token)
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error al intentar unirse a la sala. Verifica tu código de invitación.")

async def proxy_leave_room(http_client: httpx.AsyncClient, room_id: UUID, raw_token: str) -> MemberResponse:
    try:
        return await rooms_client.leave_room(http_client, room_id, raw_token)
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error al intentar salir de la sala.")