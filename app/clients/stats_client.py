import os
from app.clients.base import get_http_client
import httpx
import msgspec
from app.domain.structs import SyncPayload, SyncSessionResponse, ReportFilters, SessionReportResponse

STATS_URL = os.getenv("STATS_SERVICE_URL","http://127.0.0.1:8002")

async def process_batch_sessions(
    client: httpx.AsyncClient,
    payload: SyncPayload,
    raw_token: str
) -> SyncSessionResponse:
    url = f"{STATS_URL}/api/v1/sessions/batch"
    headers = {"Authorization": f"Bearer {raw_token}", "Content-Type": "application/json"}
    content = msgspec.json.encode(payload)
    response = await client.post(url, content=content, headers=headers)
    response.raise_for_status()
    return msgspec.json.decode(response.content, type=SyncSessionResponse)

async def fetch_session_reports(
    client: httpx.AsyncClient,
    filters: ReportFilters,
    raw_token: str
) -> SessionReportResponse:
    url = f"{STATS_URL}/api/v1/sessions/reports"
    headers = {"Authorization": f"Bearer {raw_token}"}
    
    query_params = {
        "user_id": str(filters.user_id) if filters.user_id else None,
        "room_id": str(filters.room_id) if filters.room_id else None,
        "start_date": filters.start_date.isoformat() if filters.start_date else None,
        "end_date": filters.end_date.isoformat() if filters.end_date else None,
        "sort_order": filters.sort_order,
        "limit": filters.limit,
        "offset": filters.offset
    }
    clean_filters = {k: v for k, v in query_params.items() if v is not None}

    response = await client.get(url, headers=headers, params=clean_filters)
    response.raise_for_status()
    
    return msgspec.json.decode(response.content, type=SessionReportResponse)


async def fetch_admin_kpis(
    client: httpx.AsyncClient,
    raw_token: str
) -> dict:
    """
    Solicita al microservicio de estadísticas los KPIs globales
    para el panel de administración web.
    """
    url = f"{STATS_URL}/api/v1/sessions/admin/kpis"
    headers = {"Authorization": f"Bearer {raw_token}"}

    response = await client.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()