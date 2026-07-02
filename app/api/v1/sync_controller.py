from litestar import Controller, post
from litestar.datastructures import State
from app.domain.structs import SyncPayload, SyncResponse
from app.services.sync_service import orchestrate_sync
from litestar.di import Provide
from app.dependencies.auth import provide_raw_token

class SyncController(Controller):
    path = "/sync"
    tags = ["Sincronización"]
    
    dependencies = {"raw_token": Provide(provide_raw_token, sync_to_thread=False)}

    @post()
    async def sync_offline_data(
        self,
        raw_token: str,
        state: State,
        data: SyncPayload
    ) -> SyncResponse:
        return await orchestrate_sync(
            http_client=state.http_client,
            data=data,
            raw_token=raw_token
        )