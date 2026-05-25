from fastapi import Request, HTTPException, status
# Use absolute import from the project root
from src.dependencies import rate_limit_script

async def rate_limit_middleware(request: Request, call_next):
    user_id = request.headers.get("X-API-KEY") or request.client.host
    
    # Capacity=10, Refill=1 per second
    allowed = rate_limit_script(keys=[user_id], args=[10, 1])
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded."
        )
    
    return await call_next(request)