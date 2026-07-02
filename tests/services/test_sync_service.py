import pytest
import httpx
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
from app.services.sync_service import orchestrate_sync
from app.domain.structs import (
    SyncPayload, SessionItem, SyncSessionResponse, BatchExpResponse, RewardItem, RoomResponse
)
from litestar.exceptions import HTTPException

@pytest.fixture
def valid_sync_payload():
    return SyncPayload(
        sessions=[
            SessionItem(
                activity_type="focus",
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc)
            )
        ]
    )

@pytest.mark.asyncio
@patch("app.services.sync_service.inv_client.grant_random_item", new_callable=AsyncMock)
@patch("app.services.sync_service.auth_client.add_batch_exp", new_callable=AsyncMock)
@patch("app.services.sync_service.stats_client.process_batch_sessions", new_callable=AsyncMock)
async def test_orchestrate_sync_level_up(
    mock_stats, mock_auth, mock_inv, 
    mock_http_client, valid_sync_payload
):

    mock_stats.return_value = SyncSessionResponse(total_exp_gained=500, time_trials_completed=0)
    mock_auth.return_value = BatchExpResponse(new_level=5, levels_gained=2, leveled_up=True,total_exp=500)

    mock_inv.return_value = RewardItem(id=uuid4(), name="Espada Épica")

    result = await orchestrate_sync(
        http_client=mock_http_client,
        data=valid_sync_payload,
        raw_token="fake_token"
    )

    assert result.total_exp == 500
    assert result.current_level == 5
    assert result.leveled_up is True
    assert len(result.rewards) == 2

    mock_auth.assert_called_once_with(
        client=mock_http_client, total_exp=500, raw_token="fake_token"
    )
    assert mock_inv.call_count == 2

@pytest.mark.asyncio
async def test_orchestrate_sync_empty_sessions(mock_http_client):
    empty_payload = SyncPayload(sessions=[])
    
    with pytest.raises(HTTPException) as exc:
        await orchestrate_sync(mock_http_client, empty_payload, "fake_token")
        
    assert exc.value.status_code == 400
    assert "empty" in exc.value.detail

@pytest.mark.asyncio
@patch("app.services.sync_service.rooms_client.get_room", new_callable=AsyncMock)
@patch("app.services.sync_service.inv_client.grant_random_item", new_callable=AsyncMock)
@patch("app.services.sync_service.auth_client.add_batch_exp", new_callable=AsyncMock)
@patch("app.services.sync_service.stats_client.process_batch_sessions", new_callable=AsyncMock)
async def test_orchestrate_sync_with_room_bonus(
    mock_stats, mock_auth, mock_inv, mock_get_room, mock_http_client
):
    room_id = uuid4()
    payload_with_room = SyncPayload(
        sessions=[
            SessionItem(
                activity_type="focus",
                start_time=datetime.now(timezone.utc),
                end_time=datetime.now(timezone.utc),
                room_id=room_id
            )
        ]
    )

    fake_room = RoomResponse(id=room_id, name="Sala", capacity=5, creator_id=uuid4(), status="active", xp_multiplier=1.5, description=None)
    mock_get_room.return_value = fake_room
    
    mock_stats.return_value = SyncSessionResponse(total_exp_gained=150, time_trials_completed=0)
    mock_auth.return_value = BatchExpResponse(new_level=2, levels_gained=0, leveled_up=False,total_exp=100)

    await orchestrate_sync(mock_http_client, payload_with_room, "fake_token")

    mock_get_room.assert_called_once_with(mock_http_client, room_id, "fake_token")
    
    payload_enviado = mock_stats.call_args.kwargs["payload"]
    assert payload_enviado.sessions[0].xp_multiplier == 1.5

@pytest.mark.asyncio
@patch("app.services.sync_service.rooms_client.get_room", new_callable=AsyncMock)
@patch("app.services.sync_service.auth_client.add_batch_exp", new_callable=AsyncMock)
@patch("app.services.sync_service.stats_client.process_batch_sessions", new_callable=AsyncMock)
async def test_orchestrate_sync_room_offline_fallback(
    mock_stats, mock_auth, mock_get_room, mock_http_client, valid_sync_payload
):
    import httpx

    mock_get_room.side_effect = httpx.RequestError("Offline")
    mock_stats.return_value = SyncSessionResponse(total_exp_gained=100, time_trials_completed=0)
    mock_auth.return_value = BatchExpResponse(new_level=2, levels_gained=0, leveled_up=False,total_exp=100)

    valid_sync_payload.sessions[0].room_id = uuid4()
    await orchestrate_sync(mock_http_client, valid_sync_payload, "token")
    assert mock_stats.call_args.kwargs["payload"].sessions[0].xp_multiplier == 1.0

@pytest.mark.asyncio
@patch("app.services.sync_service.stats_client.process_batch_sessions", new_callable=AsyncMock)
async def test_orchestrate_sync_internal_error(mock_stats, mock_http_client, valid_sync_payload):
    mock_req = httpx.Request("POST", "")
    mock_stats.side_effect = httpx.HTTPStatusError("Error", request=mock_req, response=httpx.Response(500, request=mock_req))
    
    with pytest.raises(HTTPException) as exc:
        await orchestrate_sync(mock_http_client, valid_sync_payload, "token")
    assert exc.value.status_code == 500
    