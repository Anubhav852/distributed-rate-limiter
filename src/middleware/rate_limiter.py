from fastapi import Request, HTTPException, status
from src.main import redis_client, rate_limit_script

async def rate_limit_middleware(request: Request, call_next):
    # Identify user by API key or IP address
    user_id = request.headers.get("X-API-KEY") or request.client.host
    
    # Define limits: Capacity=10, Refill=1 per second
    # These could also be pulled from a config file per user
    capacity = 10
    refill_rate = 1
    
    # Execute atomic Lua script
    # We pass user_id as the key, and capacity/refill_rate as arguments
    allowed = rate_limit_script(keys=[user_id], args=[10, 1])    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return await call_next(request)