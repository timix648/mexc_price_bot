import json
import os
STORAGE_FILE = "price_cache.json"

def load_cache():
    try:
        if os.path.exists("prices.json") and os.path.getsize("prices.json") > 0:
            with open("prices.json", "r") as f:
                return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ JSON decode error. Returning empty cache.")
    except Exception as e:
        print(f"⚠️ Unexpected error loading cache: {e}")
    return {}


def update_cache(cache):
    try:
        with open("prices.json", "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving cache: {e}")

