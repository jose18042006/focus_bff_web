import os
from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTAuth, Token
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "clave_secreta_por_defecto")

async def retrieve_user_handler(token: Token, connection: ASGIConnection) -> str:
    return token.sub

jwt_auth = JWTAuth[str](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=SECRET_KEY,
    exclude=[
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/status/health",
        "/schema",
        "/schema/swagger",
        "/schema/openapi.json",
        "/schema/redoc",
        "/schema/elements"
    ],    
)