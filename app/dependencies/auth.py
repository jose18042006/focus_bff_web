from litestar import Request

def provide_raw_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    return auth_header.replace("Bearer ", "") if auth_header else ""