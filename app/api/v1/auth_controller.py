from litestar import Controller, post
from litestar.datastructures import State
from app.domain.structs import RegisterPayload, RegisterResponse, LoginPayload, TokenResponse
from app.services.auth_service import orchestrate_register, orchestrate_login

class AuthController(Controller):
    path = "/auth"
    tags = ["Autenticación"]

    @post("/register", opt={"publico": True})
    async def register(
        self,
        state: State,
        data: RegisterPayload
    ) -> RegisterResponse:
        return await orchestrate_register(http_client=state.http_client, data=data)
        
    @post("/login", opt={"publico": True})
    async def login(
        self,
        state: State,
        data: LoginPayload
    ) -> TokenResponse:
        return await orchestrate_login(http_client=state.http_client, data=data)