#!/usr/bin/env python3
"""检查推荐缓存数据"""

import sqlite3
from pathlib import Path

base_dir = Path(__file__).parent
cache_db_path = base_dir / 'analysis' / 'recommendation_cache.db'

print(f"缓存数据库: {cache_db_path}")
print(f"存在: {cache_db_path.exists()}")
print()

if not cache_db_path.exists():
    print("缓存数据库不存在")
    exit(1)

conn = sqlite3.connect(str(cache_db_path))
cursor = conn.cursor()

# 查看语义评分缓存
print("=" * 80)
print("语义评分缓存 (semantic_scores_cache)")
print("=" * 80)
cursor.execute('''
    SELECT topic, record_id, topic_relevance, audience_match,
           style_fit, performance_bonus, final_score, scored_at
    FROM semantic_scores_cache
    ORDER BY scored_at DESC
    LIMIT 20
''')

rows = cursor.fetchall()
print(f"找到 {len(rows)} 条记录\n")

for row in rows:
    topic, record_id, tr, am, sf, pb, final, scored_at = row
    print(f"主题: {topic}")
    print(f"记录: {record_id}")
    print(f"  主题相关度: {tr}")
    print(f"  目标用户匹配: {am}")
    print(f"  内容风格适配: {sf}")
    print(f"  数据表现加分: {pb}")
    print(f"  最终得分: {final}")
    print(f"  评分时间: {scored_at}")
    print()

# 查看有"秋冬"的记录
print("=" * 80)
print("包含'秋冬'的评分记录")
print("=" * 80)
cursor.execute('''
    SELECT topic, record_id, topic_relevance, audience_match,
           style_fit, performance_bonus, final_score, scored_at
    FROM semantic_scores_cache
    WHERE topic LIKE '%秋冬%'
    ORDER BY scored_at DESC
''')

rows = cursor.fetchall()
print(f"找到 {len(rows)} 条记录\n")

for row in rows:
    topic, record_id, tr, am, sf, pb, final, scored_at = row
    print(f"主题: {topic}")
    print(f"记录: {record_id}")
    print(f"  主题相关度: {tr}")
    print(f"  目标用户匹配: {am}")
    print(f"  内容风格适配: {sf}")
    print(f"  数据表现加分: {pb}")
    print(f"  最终得分: {final}")
    print(f"  归一化分数: {final/10}")
    print(f"  匹配等级: {'高度匹配' if final/10 >= 0.7 else '相关推荐' if final/10 >= 0.4 else '可能相关'}")
    print(f"  评分时间: {scored_at}")
    print()

conn.close()
