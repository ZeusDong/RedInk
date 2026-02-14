"""检查数据库表结构"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent.parent / 'analysis' / 'analysis.db'
print(f"Database: {db_path}")

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# 检查 analysis_results 表结构
cursor.execute('PRAGMA table_info(analysis_results)')
columns = cursor.fetchall()

print("\n=== analysis_results 表结构 ===")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# 检查是否有推荐洞察字段
has_recommend = any(col[1] == 'recommend_reasons' for col in columns)
has_learnable = any(col[1] == 'learnable_elements' for col in columns)

print(f"\n推荐理由字段 (recommend_reasons): {'✓ 存在' if has_recommend else '✗ 不存在'}")
print(f"可学习元素字段 (learnable_elements): {'✓ 存在' if has_learnable else '✗ 不存在'}")

conn.close()
