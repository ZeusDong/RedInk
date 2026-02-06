"""Debug script to check cover image handling"""
import sys
sys.path.insert(0, 'd:\\cydprojects\\python\\RedInk')

import json
from backend.models.reference_models import transform_feishu_record

# Load cache file
with open('reference_cache/xhsKeywordSearch_cache.json', 'r', encoding='utf-8') as f:
    cache_data = json.load(f)

records = cache_data.get('records', [])
print(f"Total records in cache: {len(records)}\n")

# Check first record
if len(records) > 0:
    first_record = records[0]
    fields = first_record.get('fields', {})

    print("=== First Record Fields ===")
    print(f"Has 博主头像: {'博主头像' in fields}")
    print(f"Has 博主头像-text: {'博主头像-text' in fields}")
    print(f"Has 笔记封面: {'笔记封面' in fields}")
    print(f"Has 笔记封面-text: {'笔记封面-text' in fields}")

    # Check values
    avatar_text_val = fields.get('博主头像-text')
    cover_text_val = fields.get('笔记封面-text')
    cover_val = fields.get('笔记封面')

    print(f"\n博主头像-text value type: {type(avatar_text_val)}")
    print(f"笔记封面-text value type: {type(cover_text_val)}")
    print(f"笔记封面 value type: {type(cover_val)}")

    # Transform record
    print("\n=== Transformed Record ===")
    transformed = transform_feishu_record(first_record)
    print(f"Avatar URL: {transformed.blogger.avatar[:100] if transformed.blogger.avatar else 'None'}...")
    print(f"Cover Image URL: {transformed.cover_image[:100] if transformed.cover_image else 'None'}...")
    print(f"Images count: {len(transformed.images)}")

    # Check if avatar uses proxy
    if '/api/reference/image/' in transformed.blogger.avatar:
        print("✓ Avatar is using proxy URL")
    else:
        print("✗ Avatar is using direct URL")

    # Check if cover uses proxy
    if '/api/reference/image/' in transformed.cover_image:
        print("✓ Cover is using proxy URL")
    else:
        print("✗ Cover is using direct URL")
