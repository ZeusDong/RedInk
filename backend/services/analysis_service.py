"""
对标分析服务

负责管理待分析笔记列表的 SQLite 存储、查询、更新和删除。
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class AnalysisService:
    """对标分析服务 - 使用 SQLite 存储"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 防止重复初始化
        if hasattr(self, '_initialized'):
            logger.debug("[ANALYSIS_SERVICE] Service already initialized, skipping")
            return
        self._initialized = True

        # 数据库路径（项目根目录/analysis/analysis.db）
        self.db_dir = Path(__file__).parent.parent.parent / 'analysis'
        logger.info(f"[ANALYSIS_SERVICE] Database directory: {self.db_dir}")
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / 'analysis.db'
        logger.info(f"[ANALYSIS_SERVICE] Database path: {self.db_path}")

        # 使用线程本地存储连接（必须在 _init_db 之前初始化）
        self._local = threading.local()
        logger.debug("[ANALYSIS_SERVICE] Thread-local storage initialized")

        # 初始化数据库
        self._init_db()
        logger.info("[ANALYSIS_SERVICE] Database initialized successfully")

    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地数据库连接"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        """初始化数据库表"""
        logger.debug("[ANALYSIS_SERVICE] Initializing database tables...")
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建待分析笔记表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT NOT NULL UNIQUE,
                title TEXT,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建分析结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT NOT NULL UNIQUE,
                analyzed BOOLEAN DEFAULT 0,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pending_notes_record_id
            ON pending_notes(record_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analysis_results_record_id
            ON analysis_results(record_id)
        ''')

        conn.commit()

    def add_pending_note(self, record: Dict[str, Any]) -> bool:
        """
        添加待分析笔记

        Args:
            record: ReferenceRecord 数据

        Returns:
            bool: 是否添加成功（已存在则返回 False）
        """
        record_id = record.get('record_id', 'unknown')
        logger.debug(f"[ANALYSIS_SERVICE] Adding pending note: record_id={record_id}")

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR IGNORE INTO pending_notes (record_id, title, data)
                VALUES (?, ?, ?)
            ''', (record['record_id'], record.get('title', ''), json.dumps(record, ensure_ascii=False)))
            conn.commit()
            result = cursor.rowcount > 0
            logger.debug(f"[ANALYSIS_SERVICE] Add pending note result: record_id={record_id}, inserted={result}, rowcount={cursor.rowcount}")
            return result
        except sqlite3.Error as e:
            logger.error(f"[ANALYSIS_SERVICE] Error adding pending note (record_id={record_id}): {e}", exc_info=True)
            return False

    def add_pending_notes(self, records: List[Dict[str, Any]]) -> int:
        """
        批量添加待分析笔记

        Args:
            records: ReferenceRecord 数据列表

        Returns:
            int: 实际添加的数量
        """
        logger.info(f"[ANALYSIS_SERVICE] Adding {len(records)} pending notes (batch)")
        count = 0
        for i, record in enumerate(records):
            if self.add_pending_note(record):
                count += 1
        logger.info(f"[ANALYSIS_SERVICE] Batch add complete: {count}/{len(records)} notes added")
        return count

    def remove_pending_note(self, record_id: str) -> bool:
        """
        移除待分析笔记

        Args:
            record_id: 笔记 ID

        Returns:
            bool: 是否删除成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM pending_notes WHERE record_id = ?', (record_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error removing pending note: {e}")
            return False

    def clear_pending_notes(self) -> bool:
        """
        清空所有待分析笔记

        Returns:
            bool: 是否成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM pending_notes')
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error clearing pending notes: {e}")
            return False

    def get_pending_notes(self) -> List[Dict[str, Any]]:
        """
        获取所有待分析笔记

        Returns:
            List[Dict]: 笔记列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT data FROM pending_notes ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [json.loads(row['data']) for row in rows]
        except sqlite3.Error as e:
            print(f"Error getting pending notes: {e}")
            return []

    def get_pending_count(self) -> int:
        """
        获取待分析笔记数量

        Returns:
            int: 数量
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT COUNT(*) as count FROM pending_notes')
            row = cursor.fetchone()
            return row['count'] if row else 0
        except sqlite3.Error as e:
            print(f"Error getting pending count: {e}")
            return 0

    def is_pending(self, record_id: str) -> bool:
        """
        检查笔记是否在待分析列表中

        Args:
            record_id: 笔记 ID

        Returns:
            bool: 是否存在
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT 1 FROM pending_notes WHERE record_id = ?', (record_id,))
            return cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Error checking pending note: {e}")
            return False

    # 分析结果相关方法

    def get_analysis_result(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        获取笔记的分析结果

        Args:
            record_id: 笔记 ID

        Returns:
            Optional[Dict]: 分析结果，不存在则返回 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT record_id, analyzed, content, created_at, updated_at
                FROM analysis_results
                WHERE record_id = ?
            ''', (record_id,))
            row = cursor.fetchone()

            if row:
                return {
                    'record_id': row['record_id'],
                    'analyzed': bool(row['analyzed']),
                    'content': row['content'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
        except sqlite3.Error as e:
            print(f"Error getting analysis result: {e}")
            return None

    def set_analysis_result(self, record_id: str, analyzed: bool, content: Optional[str] = None) -> bool:
        """
        设置笔记的分析结果

        Args:
            record_id: 笔记 ID
            analyzed: 是否已分析
            content: 分析内容

        Returns:
            bool: 是否成功
        """
        logger.debug(f"[ANALYSIS_SERVICE] Setting analysis result: record_id={record_id}, analyzed={analyzed}, has_content={content is not None}")
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT OR REPLACE INTO analysis_results (record_id, analyzed, content, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (record_id, 1 if analyzed else 0, content))
            conn.commit()
            logger.info(f"[ANALYSIS_SERVICE] Analysis result saved successfully: record_id={record_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"[ANALYSIS_SERVICE] Error setting analysis result (record_id={record_id}): {e}", exc_info=True)
            return False

    def get_all_analysis_results(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有分析结果

        Returns:
            Dict[str, Dict]: 以 record_id 为键的分析结果字典
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT record_id, analyzed, content, created_at, updated_at
                FROM analysis_results
            ''')
            rows = cursor.fetchall()

            results = {}
            for row in rows:
                results[row['record_id']] = {
                    'record_id': row['record_id'],
                    'analyzed': bool(row['analyzed']),
                    'content': row['content'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return results
        except sqlite3.Error as e:
            print(f"Error getting all analysis results: {e}")
            return {}


# 全局单例
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    """获取分析服务单例"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service
