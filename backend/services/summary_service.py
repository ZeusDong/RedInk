"""
AI总结服务

负责管理AI总结的 SQLite 存储、查询、生成和删除。
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator

logger = logging.getLogger(__name__)


class SummaryService:
    """AI总结服务 - 使用 SQLite 存储"""

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
            logger.debug("[SUMMARY_SERVICE] Service already initialized, skipping")
            return
        self._initialized = True

        # 数据库路径（与 analysis_service 共享同一个数据库文件）
        self.db_dir = Path(__file__).parent.parent.parent / 'analysis'
        logger.info(f"[SUMMARY_SERVICE] Database directory: {self.db_dir}")
        self.db_path = self.db_dir / 'analysis.db'
        logger.info(f"[SUMMARY_SERVICE] Database path: {self.db_path}")

        # 使用线程本地存储连接
        self._local = threading.local()
        logger.debug("[SUMMARY_SERVICE] Thread-local storage initialized")

        # 并发控制锁（防止同一行业同时生成多个总结）
        self._generation_locks = {}
        self._generation_lock = threading.Lock()

        logger.info("[SUMMARY_SERVICE] Service initialized successfully")

    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地数据库连接"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _get_industry_lock(self, industry: str) -> threading.Lock:
        """获取指定行业的并发控制锁"""
        with self._generation_lock:
            if industry not in self._generation_locks:
                self._generation_locks[industry] = threading.Lock()
            return self._generation_locks[industry]

    def create_summary(
        self,
        industry: str,
        record_ids: List[str],
        content: str
    ) -> Optional[Dict[str, Any]]:
        """
        创建新的总结记录

        Args:
            industry: 行业名称
            record_ids: 包含的笔记 ID 列表
            content: AI 生成的总结内容

        Returns:
            Optional[Dict]: 创建的总结记录，失败返回 None
        """
        logger.info(f"[SUMMARY_SERVICE] Creating summary for industry={industry}, records={len(record_ids)}")

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO analysis_summaries (industry, record_ids, content, record_count)
                VALUES (?, ?, ?, ?)
            ''', (industry, json.dumps(record_ids, ensure_ascii=False), content, len(record_ids)))
            conn.commit()

            summary_id = cursor.lastrowid
            logger.info(f"[SUMMARY_SERVICE] Summary created: id={summary_id}, industry={industry}")

            return self.get_summary(summary_id)
        except sqlite3.Error as e:
            logger.error(f"[SUMMARY_SERVICE] Error creating summary: {e}", exc_info=True)
            return None

    def get_summary(self, summary_id: int) -> Optional[Dict[str, Any]]:
        """
        获取指定 ID 的总结

        Args:
            summary_id: 总结 ID

        Returns:
            Optional[Dict]: 总结记录，不存在返回 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, industry, record_ids, content, record_count, created_at, updated_at
                FROM analysis_summaries
                WHERE id = ?
            ''', (summary_id,))
            row = cursor.fetchone()

            if row:
                return {
                    'id': row['id'],
                    'industry': row['industry'],
                    'record_ids': json.loads(row['record_ids']),
                    'content': row['content'],
                    'record_count': row['record_count'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
            return None
        except sqlite3.Error as e:
            logger.error(f"[SUMMARY_SERVICE] Error getting summary: {e}", exc_info=True)
            return None

    def get_all_summaries(self) -> List[Dict[str, Any]]:
        """
        获取所有总结（按行业分组）

        Returns:
            List[Dict]: 总结列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, industry, record_ids, content, record_count, created_at, updated_at
                FROM analysis_summaries
                ORDER BY created_at DESC
            ''')
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'industry': row['industry'],
                    'record_ids': json.loads(row['record_ids']),
                    'content': row['content'],
                    'record_count': row['record_count'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            return results
        except sqlite3.Error as e:
            logger.error(f"[SUMMARY_SERVICE] Error getting all summaries: {e}", exc_info=True)
            return []

    def get_summaries_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """
        获取指定行业的所有总结

        Args:
            industry: 行业名称

        Returns:
            List[Dict]: 总结列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, industry, record_ids, content, record_count, created_at, updated_at
                FROM analysis_summaries
                WHERE industry = ?
                ORDER BY created_at DESC
            ''', (industry,))
            rows = cursor.fetchall()

            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'industry': row['industry'],
                    'record_ids': json.loads(row['record_ids']),
                    'content': row['content'],
                    'record_count': row['record_count'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            return results
        except sqlite3.Error as e:
            logger.error(f"[SUMMARY_SERVICE] Error getting summaries by industry: {e}", exc_info=True)
            return []

    def get_industries(self) -> List[str]:
        """
        获取所有有总结的行业列表

        Returns:
            List[str]: 行业名称列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT DISTINCT industry FROM analysis_summaries ORDER BY industry')
            rows = cursor.fetchall()
            return [row['industry'] for row in rows]
        except sqlite3.Error as e:
            logger.error(f"[SUMMARY_SERVICE] Error getting industries: {e}", exc_info=True)
            return []

    def delete_summary(self, summary_id: int) -> bool:
        """
        删除指定总结

        Args:
            summary_id: 总结 ID

        Returns:
            bool: 是否成功
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM analysis_summaries WHERE id = ?', (summary_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"[SUMMARY_SERVICE] Error deleting summary: {e}", exc_info=True)
            return False

    def generate_summary(
        self,
        industry: str,
        record_ids: List[str]
    ) -> Generator[Dict[str, Any], None, None]:
        """
        生成 AI 总结（流式输出）

        Args:
            industry: 行业名称
            record_ids: 要总结的笔记 ID 列表

        Yields:
            Dict with event type and data:
            - {"event": "progress", "data": {"step": ..., "message": ...}}
            - {"event": "complete", "data": {"id": ..., "industry": ..., "content": ...}}
            - {"event": "error", "data": {"error": ...}}
            - {"event": "finish", "data": {"record_ids": ...}}
        """
        from backend.utils.text_client import get_text_chat_client
        from backend.prompts.summary_prompts import format_summary_prompt
        from backend.config import Config
        from backend.services.analysis_service import get_analysis_service

        # 获取行业锁（防止并发）
        industry_lock = self._get_industry_lock(industry)
        acquired = industry_lock.acquire(blocking=False)

        if not acquired:
            yield {
                "event": "error",
                "data": {"error": f"该行业（{industry}）正在生成总结，请稍后再试"}
            }
            return

        try:
            yield {
                "event": "progress",
                "data": {"step": "preparing", "message": "准备生成总结..."}
            }

            # 获取分析服务
            analysis_service = get_analysis_service()

            # 获取所有笔记的分析结果
            analysis_reports = []
            for record_id in record_ids:
                result = analysis_service.get_analysis_result(record_id)
                if result and result.get('analyzed') and result.get('content'):
                    analysis_reports.append(result['content'])

            if not analysis_reports:
                yield {
                    "event": "error",
                    "data": {"error": "选中的笔记都没有分析结果，无法生成总结"}
                }
                return

            yield {
                "event": "progress",
                "data": {"step": "analyzing", "message": f"正在分析 {len(analysis_reports)} 篇笔记..."}
            }

            # 格式化提示词
            prompt = format_summary_prompt(industry, analysis_reports)

            # 获取文本生成客户端
            text_config = Config.get_text_provider_config()
            text_client = get_text_chat_client(text_config)

            yield {
                "event": "progress",
                "data": {"step": "generating", "message": "AI 正在生成总结..."}
            }

            # 调用 AI 生成总结
            summary_content = text_client.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_output_tokens=8000
            )

            yield {
                "event": "progress",
                "data": {"step": "saving", "message": "正在保存总结..."}
            }

            # 保存到数据库
            summary = self.create_summary(industry, record_ids, summary_content)

            if not summary:
                yield {
                    "event": "error",
                    "data": {"error": "保存总结失败"}
                }
                return

            # 更新笔记状态为 summarized
            analysis_service.batch_update_status(record_ids, 'summarized')

            yield {
                "event": "complete",
                "data": {
                    "id": summary['id'],
                    "industry": industry,
                    "content": summary_content
                }
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[SUMMARY_SERVICE] Summary generation failed: {error_msg}", exc_info=True)
            yield {
                "event": "error",
                "data": {"error": error_msg}
            }
        finally:
            # 释放行业锁
            industry_lock.release()
            yield {
                "event": "finish",
                "data": {"record_ids": record_ids}
            }


# 全局单例
_summary_service: Optional[SummaryService] = None


def get_summary_service() -> SummaryService:
    """获取总结服务单例"""
    global _summary_service
    if _summary_service is None:
        _summary_service = SummaryService()
    return _summary_service
