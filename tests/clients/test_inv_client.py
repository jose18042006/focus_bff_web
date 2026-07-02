import pytest
import httpx
import respx
import msgspec
import jwt
from uuid import uuid4
from app.clients.inv_client import grant_random_item, INV_URL, MSItemResponse

@pytest.mark.asyncio
@respx.mock
async def test_grant_random_item_success():
    user_id = uuid4()
    item_id = uuid4()
    
    fake_token = jwt.encode({"sub": str(user_id)}, "secret", algorithm="HS256")
    
    mock_item_response = MSItemResponse(id=item_id, name="Amuleto de Concentración")
    respx.get(f"{INV_URL}/items/random").mock(
        return_value=httpx.Response(200, content=msgspec.json.encode(mock_item_response))
    )
    
    respx.post(f"{INV_URL}/inventory").mock(
        return_value=httpx.Response(201, content=b"{}")
    )
    
    async with httpx.AsyncClient() as http_client:
        reward = await grant_random_item(http_client, fake_token)
        
    assert reward.name == "Amuleto de Concentración"
    assert reward.id == item_id

@pytest.mark.asyncio
@respx.mock
async def test_grant_random_item_fails_fast_on_404():
    user_id = uuid4()
    fake_token = jwt.encode({"sub": str(user_id)}, "secret", algorithm="HS256")
    
    respx.get(f"{INV_URL}/items/random").mock(return_value=httpx.Response(404))
    
    async with httpx.AsyncClient() as http_client:
        with pytest.raises(httpx.HTTPStatusError) as exc:
            await grant_random_item(http_client, fake_token)
            
        assert exc.value.response.status_code == 404