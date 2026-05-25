from fastapi import FastAPI
import redis
import os
from src.middleware.rate_limiter import rate_limit_middleware

app = FastAPI()


# Move the Redis connection and script loading to a central place 
# or keep them here as you have them.
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

script_path = os.path.join("src", "scripts", "rate_limit.lua")
with open(script_path, "r") as f:
    lua_script = f.read()

rate_limit_script = redis_client.register_script(lua_script)

# Apply the middleware
app.middleware("http")(rate_limit_middleware)

@app.get("/api/resource")
async def get_resource():
    return {"data": "You successfully accessed the protected resource"}