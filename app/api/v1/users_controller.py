from litestar import Controller, get
from litestar.datastructures import State
from litestar.di import Provide

from app.domain.structs import UserStatsResponse
# Asegúrate de importar tu función desde el archivo correcto
from app.services.users_service import orchestrate_get_my_stats 
from app.dependencies.auth import provide_raw_token

class UsersController(Controller):
    path = "/users"

    dependencies = {"raw_token": Provide(provide_raw_token, sync_to_thread=False)}

    @get("/me/stats")
    async def get_my_stats(
        self,
        raw_token: str,
        state: State
    ) -> UserStatsResponse:
        
        return await orchestrate_get_my_stats(
            http_client=state.http_client,
            raw_token=raw_token
        )