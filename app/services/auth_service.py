import httpx
from app.core.exceptions import handle_httpx_error
from app.domain.structs import RegisterPayload, RegisterResponse, LoginPayload, TokenResponse
from app.clients.auth_client import proxy_register, proxy_login

async def orchestrate_register(
    http_client: httpx.AsyncClient,
    data: RegisterPayload
) -> RegisterResponse:
    try:
        return await proxy_register(client=http_client, payload=data)
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Error en el registro (¿correo duplicado?)")
    
async def orchestrate_login(
    http_client: httpx.AsyncClient,
    data: LoginPayload
) -> TokenResponse:
    try:
        return await proxy_login(client=http_client, payload=data)
    except httpx.HTTPError as e:
        handle_httpx_error(e, "Credenciales inválidas")