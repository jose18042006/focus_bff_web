import httpx
from uuid import UUID
from litestar.exceptions import HTTPException, PermissionDeniedException

from app.clients.stats_client import fetch_session_reports
from app.clients.rooms_client import get_room
from app.domain.structs import SessionReportResponse, ReportFilters
from app.core.exceptions import handle_httpx_error

async def orchestrate_session_reports(
    http_client: httpx.AsyncClient,
    filters: ReportFilters,
    raw_token: str,
    logged_user_id: UUID,
    user_role: str
) -> SessionReportResponse:
    
    if filters.user_id and filters.user_id != logged_user_id and user_role == "student":
        raise PermissionDeniedException("No tienes permiso para ver los informes de otro usuario.")
    
    if filters.room_id:
        if user_role == "student":
            raise PermissionDeniedException("Los estudiantes no pueden solicitar informes de salas enteras.")
        elif user_role == "dm":
            try:
                room_info = await get_room(
                    client=http_client, 
                    room_id=filters.room_id, 
                    raw_token=raw_token
                )
                
                if room_info.creator_id != logged_user_id:
                    raise PermissionDeniedException("Solo puedes ver estadísticas de las salas que has creado.")
                    
            except httpx.HTTPError as e:
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 404:
                    raise HTTPException(detail="La sala solicitada no existe.", status_code=404)
                handle_httpx_error(e, "Error al consultar la sala.")
    
    try:
        return await fetch_session_reports(client=http_client, filters=filters, raw_token=raw_token)
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error en MS Stats.")