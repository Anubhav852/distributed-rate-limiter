import redis
import os
import logging
import json
from datetime import datetime

# Setup JSON Logger
logging.basicConfig(level=logging.INFO)
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {"timestamp": datetime.utcnow().isoformat(), "level": record.levelname, "message": record.getMessage()}
        return json.dumps(log_record)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("enterprise_logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Redis Config
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0, decode_responses=True)
redis_client = redis.Redis(connection_pool=pool)

script_path = os.path.join("src", "scripts", "rate_limit.lua")
with open(script_path, "r") as f:
    lua_script = f.read()
rate_limit_script = redis_client.register_script(lua_script)