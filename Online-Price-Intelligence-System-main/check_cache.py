
import json
import redis
import os

def check_cache(query):
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", 6379))
    client = redis.Redis(host=host, port=port, db=0, decode_responses=True)
    
    q_key = " ".join(query.strip().split()).lower()
    keys = [f"compare_{q_key}", f"search_{q_key}"]
    
    for key in keys:
        data = client.get(key)
        if data:
            print(f"CACHE KEY: {key}")
            parsed = json.loads(data)
            products = parsed.get("products", [])
            for p in products[:5]:
                print(f"  - {p.get('platform')}: {p.get('price')} | {p.get('title')}")
        else:
            print(f"CACHE KEY: {key} (NOT FOUND)")

if __name__ == "__main__":
    check_cache("Running Shoes")
