import httpx
from app.core.exceptions import handle_httpx_error
from app.domain.structs import UserStatsResponse
from app.clients.auth_client import get_my_level_and_exp
async def orchestrate_get_my_stats(
    http_client: httpx.AsyncClient,
    raw_token: str
) -> UserStatsResponse:
    try:
        return await get_my_level_and_exp(
            client=http_client, 
            raw_token=raw_token
        )
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error al obtener las estadísticas del usuario.")