"""
数据库迁移脚本：添加推荐洞察字段到 analysis_results 表

执行方式：
    python -m backend.scripts.migrate_add_insights_fields.py
"""

import logging
import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """检查列是否存在"""
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
            SELECT {column} FROM {table} LIMIT 1
        ''')
        return True
    except sqlite3.OperationalError:
        return False


def migrate():
    """执行数据库迁移"""
    db_path = project_root / 'analysis' / 'analysis.db'

    if not db_path.exists():
        logger.error(f"Database not found at: {db_path}")
        return False

    logger.info(f"Starting migration for database: {db_path}")

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # 检查列是否已存在
        has_recommend_reasons = check_column_exists(conn, 'analysis_results', 'recommend_reasons')
        has_learnable_elements = check_column_exists(conn, 'analysis_results', 'learnable_elements')

        if has_recommend_reasons and has_learnable_elements:
            logger.info("Migration already completed (columns exist)")
            return True

        # 添加 recommend_reasons 列
        if not has_recommend_reasons:
            logger.info("Adding column: recommend_reasons")
            cursor.execute('''
                ALTER TABLE analysis_results ADD COLUMN recommend_reasons TEXT
            ''')
            logger.info("Column recommend_reasons added successfully")
        else:
            logger.info("Column recommend_reasons already exists, skipping")

        # 添加 learnable_elements 列
        if not has_learnable_elements:
            logger.info("Adding column: learnable_elements")
            cursor.execute('''
                ALTER TABLE analysis_results ADD COLUMN learnable_elements TEXT
            ''')
            logger.info("Column learnable_elements added successfully")
        else:
            logger.info("Column learnable_elements already exists, skipping")

        # 创建索引（可选，用于按推荐质量排序）
        logger.info("Creating index: idx_analysis_results_recommended")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analysis_results_recommended
            ON analysis_results(analyzed, updated_at)
        ''')

        conn.commit()
        logger.info("Migration completed successfully")

        # 显示当前表结构
        cursor.execute('PRAGMA table_info(analysis_results)')
        columns = cursor.fetchall()
        logger.info("Current analysis_results table structure:")
        for col in columns:
            logger.info(f"  - {col[1]} ({col[2]})")

        return True

    except sqlite3.Error as e:
        logger.error(f"Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
