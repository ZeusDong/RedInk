"""Delete cache files to force regeneration"""
import os

cache_dir = r"d:\cydprojects\python\RedInk\reference_cache"

# List of cache files to delete
cache_files = [
    os.path.join(cache_dir, "xhsKeywordSearch_cache.json"),
    os.path.join(cache_dir, "default_cache.json"),
]

for cache_file in cache_files:
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print(f"Deleted: {cache_file}")
    else:
        print(f"Not found: {cache_file}")

print("\nCache files deleted. Please restart the backend server and sync data.")
