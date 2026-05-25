import asyncio
from src.core.config import redis_client, rate_limit_script

async def check_rate_limit(user_id: str, limit: int = 10) -> bool:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, rate_limit_script, [user_id], [limit])
    return int(result) == 1