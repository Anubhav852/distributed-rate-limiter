from src.dependencies import redis_client

# Clear the rate limit key
key_to_delete = "127.0.0.1"
result = redis_client.delete(key_to_delete)

if result:
    print(f"Successfully reset '{key_to_delete}'")
else:
    print(f"Key '{key_to_delete}' not found, nothing to reset.")