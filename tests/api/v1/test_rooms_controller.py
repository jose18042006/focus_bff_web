import pytest
from unittest.mock import patch
from litestar.testing import TestClient
from litestar import Litestar
from uuid import uuid4

from app.api.v1.rooms_controller import RoomsController 
from app.domain.structs import RoomResponse, MemberResponse
from litestar.datastructures import State
from unittest.mock import MagicMock

app_test = Litestar(
    route_handlers=[RoomsController],
    state=State({"http_client": MagicMock()}) 
)

@patch("app.api.v1.rooms_controller.rooms_service.proxy_get_room")
def test_controller_get_room(mock_proxy_get_room):
    room_id_str = str(uuid4())
    fake_room = RoomResponse(id=uuid4(), name="Test", capacity=5, creator_id=uuid4(), status="active", xp_multiplier=1.0, description=None)
    
    mock_proxy_get_room.return_value = fake_room

    with TestClient(app=app_test) as client:
        response = client.get(
            f"/rooms/{room_id_str}",
            headers={"Authorization": "Bearer el_token_secreto"}
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Test"

    mock_proxy_get_room.assert_called_once()
    
    llamada_argumentos = mock_proxy_get_room.call_args.args
    
    assert llamada_argumentos[2] == "el_token_secreto"

@patch("app.api.v1.rooms_controller.rooms_service.proxy_create_room")
def test_controller_create_room(mock_proxy_create):
    fake_room = RoomResponse(id=uuid4(), name="Mi Sala", capacity=5, creator_id=uuid4(), status="active", xp_multiplier=1.0, description=None)
    mock_proxy_create.return_value = fake_room

    with TestClient(app=app_test) as client:
        response = client.post(
            "/rooms/",
            json={"name": "Mi Sala", "capacity": 5, "xp_multiplier": 1.0},
            headers={"Authorization": "Bearer token_post"}
        )

    assert response.status_code == 201
    assert response.json()["name"] == "Mi Sala"
    
    # Validar inyección del token
    mock_proxy_create.assert_called_once()
    assert mock_proxy_create.call_args.args[2] == "token_post"

@patch("app.api.v1.rooms_controller.rooms_service.proxy_join_room")
def test_controller_join_room(mock_proxy_join):
    mock_proxy_join.return_value = MemberResponse(message="Unido", room_id=uuid4())

    with TestClient(app=app_test) as client:
        response = client.post(
            "/rooms/join",
            json={"invitation_code": "FOCUS2026"},
            headers={"Authorization": "Bearer token_join"}
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Unido"
    assert mock_proxy_join.call_args.args[2] == "token_join"

@patch("app.api.v1.rooms_controller.rooms_service.proxy_get_all_rooms")
def test_controller_list_rooms(mock_proxy_list):
    mock_proxy_list.return_value = [] 

    with TestClient(app=app_test) as client:
        response = client.get(
            "/rooms/",
            headers={"Authorization": "Bearer token_list"}
        )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert mock_proxy_list.call_args.args[1] == "token_list"

@patch("app.api.v1.rooms_controller.rooms_service.proxy_end_room")
def test_controller_end_room(mock_proxy_end):
    fake_room = RoomResponse(id=uuid4(), name="Test", capacity=5, creator_id=uuid4(), status="ended", xp_multiplier=1.0, description=None)
    mock_proxy_end.return_value = fake_room
    room_id = uuid4()

    with TestClient(app=app_test) as client:
        response = client.post(f"/rooms/{room_id}/end", headers={"Authorization": "Bearer tkn"})

    assert response.status_code == 200
    assert mock_proxy_end.call_args.args[2] == "tkn"

@patch("app.api.v1.rooms_controller.rooms_service.proxy_leave_room")
def test_controller_leave_room(mock_proxy_leave):
    mock_proxy_leave.return_value = MemberResponse(message="Left", room_id=uuid4())
    room_id = uuid4()

    with TestClient(app=app_test) as client:
        response = client.delete(f"/rooms/{room_id}/leave", headers={"Authorization": "Bearer tkn"})

    assert response.status_code == 200
    assert mock_proxy_leave.call_args.args[2] == "tkn"