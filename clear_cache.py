"""Clear cache file to force regeneration with new code"""
import os

cache_file = r"d:\cydprojects\python\RedInk\reference_cache\xhsKeywordSearch_cache.json"

if os.path.exists(cache_file):
    os.remove(cache_file)
    print(f"Deleted: {cache_file}")
else:
    print(f"File not found: {cache_file}")
