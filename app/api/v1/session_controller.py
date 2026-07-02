from uuid import UUID
from datetime import datetime
from litestar import Controller, get, Request
from litestar.datastructures import State
from typing import Optional, Annotated
from litestar.params import QueryParameter
from app.services.report_service import orchestrate_session_reports
from app.domain.structs import SessionReportResponse, ReportFilters
from app.dependencies.auth import provide_raw_token
from litestar.di import Provide

class SessionsReportsController(Controller):
    path = "/sessions"
    tags = ["Reportes"]

    dependencies = {"raw_token": Provide(provide_raw_token, sync_to_thread=False)}

    @get("/reports")
    async def get_reports(
        self, 
        request: Request,
        raw_token: str,
        state: State,
        limit: Annotated[int, QueryParameter()] = 50,
        sort_order: Annotated[str, QueryParameter()] = "desc",
        offset: Annotated[int, QueryParameter()] = 0,
        user_id: Annotated[Optional[UUID], QueryParameter()] = None,
        room_id: Annotated[Optional[UUID], QueryParameter()] = None,
        start_date: Annotated[Optional[datetime], QueryParameter()] = None,
        end_date: Annotated[Optional[datetime], QueryParameter()] = None
    ) -> SessionReportResponse:
        
        filters = ReportFilters(
            limit=limit,
            sort_order=sort_order,
            offset=offset,
            user_id=user_id,
            room_id=room_id,
            start_date=start_date,
            end_date=end_date
        )

        user_data = request.user
        logged_user_id = UUID(str(user_data.get("sub")))
        user_role = user_data.get("role", "student")

        return await orchestrate_session_reports(
            http_client=state.http_client,
            filters=filters,
            raw_token=raw_token,
            logged_user_id=logged_user_id,
            user_role=user_role
        )