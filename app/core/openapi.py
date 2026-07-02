from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.spec import Tag

openapi_config = OpenAPIConfig(
    title="Focus Mobile BFF (API Gateway)",
    version="1.0.0",
    description=(
        "Backend For Frontend principal para la aplicación móvil. \n\n"
        "Actúa como proxy reverso y único punto de entrada público. Se encarga de "
        "enrutar el inicio de sesión, procesar la sincronización de sesiones offline "
        "y orquestar la comunicación con los microservicios internos (Auth, Stats e Inventory)."
    ),
    tags=[
        Tag(name="Autenticación", description="Proxy de registro y login. No requieren token JWT."),
        Tag(name="Sincronización", description="Endpoints protegidos para sincronizar datos locales del dispositivo."),
        Tag(name="Reportes", description="Endpoints protegidos acerca de los reportes de actividades"),
        Tag(name="Estatus", description="Endpoints protegidos acerca de el interno del servicio"),
    ]
)