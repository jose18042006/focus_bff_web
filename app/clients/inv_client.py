import os
import httpx
import msgspec
import jwt
from uuid import UUID
from app.domain.structs import RewardItem
from app.domain.structs import MSItemResponse, MSInventoryPayload

INV_URL = os.getenv("INVENTORY_SERVICE_URL","http://127.0.0.1:8003")

async def grant_random_item(
    client: httpx.AsyncClient,
    raw_token: str
) -> RewardItem:
    
    decoded = jwt.decode(raw_token, options={"verify_signature": False})
    user_id = UUID(decoded["sub"])
    
    headers = {
        "Authorization": f"Bearer {raw_token}",
        "Content-Type": "application/json"
    }

    res_item = await client.get(f"{INV_URL}/items/random", headers=headers)
    res_item.raise_for_status()  
    item = msgspec.json.decode(res_item.content, type=MSItemResponse)

    payload = MSInventoryPayload(user_id=user_id, item_id=item.id)
    res_inv = await client.post(
        f"{INV_URL}/inventory",
        content=msgspec.json.encode(payload),
        headers=headers
    )
    res_inv.raise_for_status()  

    return RewardItem(id=item.id, name=item.name)