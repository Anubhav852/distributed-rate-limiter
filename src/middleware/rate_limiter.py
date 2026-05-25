from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.services.rate_limiter_service import check_rate_limit
import logging

logger = logging.getLogger("uvicorn.error")

async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/api/status":
        return await call_next(request)

    user_id = request.client.host if request.client else "unknown"
    
    if not await check_rate_limit(user_id):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"message": "Rate limit exceeded."}
        )
        
    return await call_next(request)