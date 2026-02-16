#!/usr/bin/env python3
"""清除语义评分缓存"""

import sqlite3
from pathlib import Path

base_dir = Path(__file__).parent
cache_db_path = base_dir / 'analysis' / 'recommendation_cache.db'

print(f"缓存数据库: {cache_db_path}")
print()

if not cache_db_path.exists():
    print("缓存数据库不存在")
    exit(0)

conn = sqlite3.connect(str(cache_db_path))
cursor = conn.cursor()

# 查看有多少记录
cursor.execute('SELECT COUNT(*) FROM semantic_scores_cache')
count = cursor.fetchone()[0]
print(f"当前语义评分缓存记录数: {count}")

# 删除所有记录
cursor.execute('DELETE FROM semantic_scores_cache')
deleted = cursor.rowcount
conn.commit()

print(f"已删除 {deleted} 条语义评分缓存记录")

conn.close()
print("\n缓存已清除，下次搜索时会重新计算评分")
