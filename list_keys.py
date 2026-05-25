from src.dependencies import redis_client

keys = redis_client.keys("*")
print(f"Keys found in Redis: {keys}")

for key in keys:
    val = redis_client.get(key)
    print(f"Key: {key}, Value: {val}")