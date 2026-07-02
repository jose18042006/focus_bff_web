import os
import uvicorn
from litestar import Litestar, Router
from dotenv import load_dotenv
from app.core.openapi import openapi_config
from app.core.security import jwt_auth
from app.api.v1.sync_controller import SyncController
from app.api.v1.auth_controller import AuthController
from app.api.v1.session_controller import SessionsReportsController
from app.api.v1.ms_status_controller import MsStatusController
from app.api.v1.rooms_controller import RoomsController
from app.api.v1.users_controller import UsersController
from app.core.lifespan import http_client_lifespan
from app.core.exceptions import GLOBAL_EXCEPTION_HANDLERS

load_dotenv()

PUERTO = int(os.getenv("LITESTAR_PORT", 8000))

api_v1_router = Router(
    path="/api/v1",
    route_handlers=[
        AuthController, 
        SyncController,
        MsStatusController,
        SessionsReportsController,
        RoomsController,
        UsersController
    ]
)

app = Litestar(
    route_handlers=[api_v1_router],
    on_app_init=[jwt_auth.on_app_init],
    openapi_config=openapi_config,
    lifespan=[http_client_lifespan],
    exception_handlers=GLOBAL_EXCEPTION_HANDLERS,
    debug=False
)

if __name__ == "__main__": # pragma: no covers
    uvicorn.run("app.main:app", host="0.0.0.0", port=PUERTO, reload=True)