from fastapi import FastAPI, Request, HTTPException
import redis
import os

app = FastAPI()

# Connect to Redis (assuming local docker-compose setup)
# In production, use env variables for host/port
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Load the Lua script
script_path = os.path.join("src", "scripts", "rate_limit.lua")
with open(script_path, "r") as f:
    lua_script = f.read()

# Register the script in Redis so we can call it by its hash
rate_limit_script = redis_client.register_script(lua_script)

@app.get("/")
async def root():
    return {"message": "Gateway operational"}

# This is a dummy protected route
@app.get("/api/resource")
async def get_resource():
    return {"data": "You successfully accessed the protected resource"}