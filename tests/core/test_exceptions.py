import pytest
import httpx
from litestar.exceptions import HTTPException
from app.core.exceptions import handle_httpx_error

def test_handle_httpx_error_status():
    mock_req = httpx.Request("GET", "")
    mock_res = httpx.Response(400, json={"detail": "Malo"}, request=mock_req)
    error = httpx.HTTPStatusError("Mensaje", request=mock_req, response=mock_res)
    
    with pytest.raises(HTTPException) as exc:
        handle_httpx_error(error)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Malo"

def test_handle_httpx_error_request():
    mock_req = httpx.Request("GET", "")
    error = httpx.RequestError("Offline", request=mock_req)
    
    with pytest.raises(HTTPException) as exc:
        handle_httpx_error(error)
    assert exc.value.status_code == 503

def test_handle_httpx_error_generic():
    error = httpx.HTTPError("Error Raro")
    with pytest.raises(HTTPException) as exc:
        handle_httpx_error(error)
    assert exc.value.status_code == 500

