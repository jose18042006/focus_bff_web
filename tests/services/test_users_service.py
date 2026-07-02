import pytest
import httpx
from unittest.mock import AsyncMock, patch as mock_patch
from litestar.exceptions import HTTPException

from app.domain.structs import UserStatsResponse
from app.services.users_service import orchestrate_get_my_stats 

@pytest.mark.asyncio
@mock_patch("app.services.users_service.get_my_level_and_exp", new_callable=AsyncMock)
async def test_orchestrate_get_my_stats_success(mock_client_call):

    mock_client_call.return_value = UserStatsResponse(total_exp=1200, current_level=6)
    dummy_http_client = httpx.AsyncClient()
    fake_token = "token_falso_123"

    result = await orchestrate_get_my_stats(
        http_client=dummy_http_client, 
        raw_token=fake_token
    )

    assert result.total_exp == 1200
    assert result.current_level == 6
    mock_client_call.assert_called_once_with(client=dummy_http_client, raw_token=fake_token)

@pytest.mark.asyncio
@mock_patch("app.services.users_service.get_my_level_and_exp", new_callable=AsyncMock)
async def test_orchestrate_get_my_stats_httpx_error(mock_client_call):

    fake_request = httpx.Request("GET", "http://fakeurl")
    mock_client_call.side_effect = httpx.HTTPStatusError(
        message="Error 404", 
        request=fake_request, 
        response=httpx.Response(404, request=fake_request)
    )
    dummy_http_client = httpx.AsyncClient()

    with pytest.raises(HTTPException) as exc_info:
        await orchestrate_get_my_stats(dummy_http_client, "token_falso")
    
    assert exc_info.value.status_code == 404