import pytest
from app.domain.structs import RoomCreate

def test_base_model_serialization():
    room = RoomCreate(name="Sala Épica", capacity=5, xp_multiplier=1.2)
    data = room.to_dict()
    assert data["name"] == "Sala Épica"
    assert data["capacity"] == 5
    
    room_recreada = RoomCreate.from_dict(data)
    assert room_recreada.name == "Sala Épica"
    assert room_recreada.xp_multiplier == 1.2