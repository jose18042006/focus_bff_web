import httpx
from litestar.exceptions import HTTPException
from litestar import status_codes
from app.clients import stats_client, auth_client, inv_client, rooms_client
from app.domain.structs import SyncPayload, SyncResponse
from app.core.exceptions import handle_httpx_error

async def orchestrate_sync(
    http_client: httpx.AsyncClient,
    data: SyncPayload, raw_token: str
) -> SyncResponse:
    
    if not data.sessions:
        raise HTTPException(
            detail="The request data provided is invalid or empty.",
            status_code=status_codes.HTTP_400_BAD_REQUEST
        )

    room_cache = {}
    for session in data.sessions:
        if session.room_id:
            room_id_str = str(session.room_id)
            if room_id_str not in room_cache:
                try:
                    room_info = await rooms_client.get_room(http_client, session.room_id, raw_token)
                    room_cache[room_id_str] = room_info.xp_multiplier if room_info.status == "active" else 1.0
                except httpx.HTTPError:
                    room_cache[room_id_str] = 1.0
            
            session.xp_multiplier = room_cache[room_id_str]

    try:
        stats_data = await stats_client.process_batch_sessions(client=http_client, payload=data, raw_token=raw_token)
        auth_data = await auth_client.add_batch_exp(
            client=http_client, 
            total_exp=stats_data.total_exp_gained, 
            raw_token=raw_token
        )
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error procesando la sincronización en los servicios internos.")

    rewards_otorgadas = []
    if auth_data.levels_gained > 0:
        for _ in range(auth_data.levels_gained):
            try:
                reward = await inv_client.grant_random_item(client=http_client, raw_token=raw_token)
                rewards_otorgadas.append(reward)
            except Exception:
                pass
    return SyncResponse(
        status="synchronized",
        processed_sessions_count=len(data.sessions),
        total_exp=auth_data.total_exp,
        total_exp_gained=stats_data.total_exp_gained,
        current_level=auth_data.new_level,
        leveled_up=auth_data.leveled_up,
        levels_gained=auth_data.levels_gained,
        rewards=rewards_otorgadas    
    )