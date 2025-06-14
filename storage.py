import json
import os

STORAGE_FILE = "price_cache.json"

def load_cache():
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ JSON decode error. Returning empty cache.")
        return {}
    except Exception as e:
        print(f"❌ Error loading cache: {e}")
        return {}

def update_cache(cache):
    try:
        with open(STORAGE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving cache: {e}")
