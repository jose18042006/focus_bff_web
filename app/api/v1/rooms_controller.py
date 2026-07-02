from uuid import UUID
from typing import Annotated, List
from litestar import Controller, post, get, delete, params
from litestar.datastructures import State
from litestar.di import Provide

from app.domain.structs import RoomResponse, RoomCreate, JoinRoomRequest, MemberResponse
from app.services import rooms_service
from app.dependencies.auth import provide_raw_token
from litestar.params import PathParameter

class RoomsController(Controller):
    path = "/rooms"
    tags = ["Salas"]

    dependencies = {"raw_token": Provide(provide_raw_token, sync_to_thread=False)}

    @post("/", status_code=201)
    async def create_room(
        self, state:
        State,
        data: RoomCreate,
        raw_token: str
    ) -> RoomResponse:
        return await rooms_service.proxy_create_room(state.http_client, data, raw_token)

    @get("/")
    async def list_rooms(
        self,
        state: State,
        raw_token: str
    ) -> List[RoomResponse]:
        return await rooms_service.proxy_get_all_rooms(state.http_client, raw_token)

    @get("/{room_id:uuid}")
    async def get_room(
        self, 
        state: State, 
        room_id: Annotated[UUID, PathParameter(title="ID de la Sala")], 
        raw_token: str
    ) -> RoomResponse:
        return await rooms_service.proxy_get_room(state.http_client, room_id, raw_token)

    @post("/{room_id:uuid}/end", status_code=200)
    async def end_room(
        self, 
        state: State, 
        room_id: Annotated[UUID, PathParameter(title="ID de la Sala")], 
        raw_token: str
    ) -> RoomResponse:
        return await rooms_service.proxy_end_room(state.http_client, room_id, raw_token)

    @post("/join", status_code=200)
    async def join_room(
        self,
        state: State,
        data: JoinRoomRequest,
        raw_token: str
    ) -> MemberResponse:
        return await rooms_service.proxy_join_room(state.http_client, data, raw_token)

    @delete("/{room_id:uuid}/leave", status_code=200)
    async def leave_room(
        self, 
        state: State, 
        room_id: Annotated[UUID, PathParameter(title="ID de la Sala")], 
        raw_token: str
    ) -> MemberResponse:
        return await rooms_service.proxy_leave_room(state.http_client, room_id, raw_token)
    
    