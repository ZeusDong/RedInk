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

        # 创建分析草稿表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT NOT NULL UNIQUE,
                data TEXT NOT NULL,
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

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_analysis_drafts_record_id
            ON analysis_drafts(record_id)
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

    # ==================== Draft Management ====================

    def get_draft(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定记录的草稿数据

        Args:
            record_id: 笔记 ID

        Returns:
            Optional[Dict]: 草稿数据，不存在则返回 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT data FROM analysis_drafts
                WHERE record_id = ?
            ''', (record_id,))
            row = cursor.fetchone()

            if row:
                return json.loads(row['data'])
            return None
        except sqlite3.Error as e:
            logger.error(f"[ANALYSIS_SERVICE] Error getting draft (record_id={record_id}): {e}")
            return None

    def save_draft(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存草稿数据

        Args:
            data: 草稿数据，包含 record_id 及其他表单字段

        Returns:
            Dict: 保存后的草稿数据
        """
        record_id = data.get('record_id')
        if not record_id:
            raise ValueError("record_id is required")

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # 准备数据
            draft_data = {
                'id': data.get('id') or self._generate_id(),
                'record_id': record_id,
                'status': 'draft',
                'industry': data.get('industry', ''),
                'follower_count': data.get('follower_count', 0),
                'published_at': data.get('published_at'),
                'likes_count': data.get('likes_count', 0),
                'saves_count': data.get('saves_count', 0),
                'comments_count': data.get('comments_count', 0),
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'visual_description': data.get('visual_description', ''),
                'top_comments': data.get('top_comments', []),
                'created_at': data.get('created_at') or datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            cursor.execute('''
                INSERT OR REPLACE INTO analysis_drafts (record_id, data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (record_id, json.dumps(draft_data, ensure_ascii=False)))
            conn.commit()

            logger.info(f"[ANALYSIS_SERVICE] Draft saved: record_id={record_id}")
            return draft_data
        except sqlite3.Error as e:
            logger.error(f"[ANALYSIS_SERVICE] Error saving draft (record_id={record_id}): {e}")
            raise

    def submit_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        提交分析（保存草稿并标记为分析中）

        Args:
            data: 分析数据

        Returns:
            Dict: 保存后的数据
        """
        record_id = data.get('record_id')
        if not record_id:
            raise ValueError("record_id is required")

        # 先保存草稿
        draft_data = self.save_draft(data)

        # 更新状态为 analyzing
        draft_data['status'] = 'analyzing'
        draft_data['updated_at'] = datetime.now().isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE analysis_drafts
                SET data = ?, updated_at = CURRENT_TIMESTAMP
                WHERE record_id = ?
            ''', (json.dumps(draft_data, ensure_ascii=False), record_id))
            conn.commit()

            logger.info(f"[ANALYSIS_SERVICE] Analysis submitted: record_id={record_id}")

            # TODO: 这里可以触发异步 AI 分析任务
            # self._trigger_ai_analysis(record_id, draft_data)

            return draft_data
        except sqlite3.Error as e:
            logger.error(f"[ANALYSIS_SERVICE] Error submitting analysis (record_id={record_id}): {e}")
            raise

    # ==================== Helper Methods ====================

    def _generate_id(self) -> str:
        """生成唯一 ID"""
        import uuid
        return str(uuid.uuid4())

    # ==================== Visual Description Generation ====================

    def generate_visual_description(
        self,
        record_id: str,
        image_indices: list[int]
    ) -> Dict[str, Any]:
        """
        AI 生成视觉描述（多图并发）

        Args:
            record_id: 笔记 ID
            image_indices: 图片索引列表（-1 表示封面图，0,1,2... 表示内容图）

        Returns:
            Dict: 包含生成的视觉描述
        """
        from backend.utils.text_client import get_text_chat_client
        from backend.config import Config
        from backend.prompts.analysis_prompts import format_image_analysis_prompt
        from backend.services.feishu_service import get_feishu_service
        import concurrent.futures

        # 获取记录数据
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT data FROM pending_notes WHERE record_id = ?', (record_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Record not found: {record_id}")

            record = json.loads(row['data'])
        except Exception as e:
            logger.error(f"[ANALYSIS_SERVICE] Error fetching record (record_id={record_id}): {e}")
            raise

        # 获取图片数据
        images_data = []
        cover_image = record.get('cover_image', '')
        content_images = record.get('images', [])

        # 构建图片列表
        images_to_analyze = []
        for idx in image_indices:
            if idx == -1 and cover_image:
                images_to_analyze.append(('封面图', cover_image))
            elif 0 <= idx < len(content_images):
                images_to_analyze.append(('内容图', content_images[idx]))

        if not images_to_analyze:
            return {'description': '', 'error': '没有有效的图片可供分析'}

        # 获取文本生成客户端
        try:
            text_config = Config.get_text_provider_config()
            text_client = get_text_chat_client(text_config)
        except Exception as e:
            logger.error(f"[ANALYSIS_SERVICE] Error getting text client: {e}")
            return {'description': '', 'error': f'获取 AI 客户端失败: {str(e)}'}

        # 并发分析图片
        results = []
        feishu_service = get_feishu_service()

        # 配置飞书服务（需要加载 OAuth 凭据以支持 token 自动刷新）
        try:
            workspace_name = Config.get_active_feishu_workspace()
            workspace_config = Config.get_feishu_workspace_config(workspace_name)
            feishu_service.configure(workspace_name, workspace_config)
            logger.debug(f"[ANALYSIS_SERVICE] Configured Feishu service for workspace: {workspace_name}")
        except Exception as e:
            logger.warning(f"[ANALYSIS_SERVICE] Failed to configure Feishu service: {e}")
            # 继续执行，因为图片可能是本地文件或外部 URL

        # 图片代理服务（用于处理小红书403反盗链问题）
        from backend.services.image_proxy_service import get_image_proxy_service
        image_proxy_service = get_image_proxy_service()

        def analyze_image(image_type: str, image_url: str) -> tuple[str, str]:
            """分析单张图片"""
            import requests
            import tempfile
            import os
            try:
                # 获取图片二进制数据
                image_bytes = None
                load_error = None

                if image_url.startswith('/api/reference/image/'):
                    # Feishu 代理 URL（封面图、头像等）
                    file_token = image_url.split('/')[-1]
                    logger.debug(f"[ANALYSIS_SERVICE] Downloading Feishu image: {file_token}")
                    image_bytes, _ = feishu_service.download_image(file_token)
                    if not image_bytes:
                        load_error = f"飞书图片下载失败 (token: {file_token})"
                elif image_url.startswith('/api/reference-images/'):
                    # 本地文件 - 上传到图床后使用图床URL
                    from backend.config import Config
                    parts = image_url.split('/')
                    rec_id, filename = parts[4], parts[5]
                    image_path = Config.get_reference_images_path() / rec_id / filename
                    logger.debug(f"[ANALYSIS_SERVICE] Local image path: {image_path}")
                    if image_path.exists():
                        # 上传到图床
                        logger.debug(f"[ANALYSIS_SERVICE] Uploading local image to proxy: {image_path}")
                        upload_success, upload_result = image_proxy_service.upload_image(str(image_path))
                        if upload_success:
                            proxy_url = upload_result
                            logger.info(f"[ANALYSIS_SERVICE] Local image uploaded to proxy: {proxy_url}")
                            # 使用图床URL获取图片
                            proxy_response = requests.get(proxy_url, timeout=30)
                            if proxy_response.status_code == 200:
                                image_bytes = proxy_response.content
                                logger.debug(f"[ANALYSIS_SERVICE] Successfully fetched image from proxy: {proxy_url}")
                            else:
                                load_error = f"图床URL请求失败 ({proxy_response.status_code})"
                                logger.warning(f"[ANALYSIS_SERVICE] {image_type} 图床URL返回{proxy_response.status_code}")
                        else:
                            load_error = f"图床上传失败: {upload_result}"
                            logger.warning(f"[ANALYSIS_SERVICE] {image_type} 图床上传失败: {upload_result}")
                    else:
                        load_error = f"本地文件不存在: {image_path}"
                else:
                    # 外部 URL - 直接使用 backend/static/reference_images/{record_id} 中的本地文件
                    logger.debug(f"[ANALYSIS_SERVICE] {image_type} 使用本地reference_images目录: {record_id}")
                    try:
                        from backend.config import Config
                        ref_images_dir = Config.get_reference_images_path() / record_id

                        if ref_images_dir.exists():
                            # 获取目录中的图片文件
                            image_files = list(ref_images_dir.glob('*.jpg')) + \
                                         list(ref_images_dir.glob('*.png')) + \
                                         list(ref_images_dir.glob('*.webp')) + \
                                         list(ref_images_dir.glob('*.gif'))

                            if image_files:
                                # 使用第一个找到的图片文件
                                local_path = image_files[0]
                                logger.debug(f"[ANALYSIS_SERVICE] Using local image: {local_path}")

                                # 上传到图床
                                upload_success, upload_result = image_proxy_service.upload_image(str(local_path))

                                if upload_success:
                                    proxy_url = upload_result
                                    logger.info(f"[ANALYSIS_SERVICE] Local image uploaded to proxy: {proxy_url}")
                                    # 使用图床URL获取图片
                                    proxy_response = requests.get(proxy_url, timeout=30)
                                    if proxy_response.status_code == 200:
                                        image_bytes = proxy_response.content
                                        logger.debug(f"[ANALYSIS_SERVICE] Successfully fetched image from proxy: {proxy_url}")
                                    else:
                                        load_error = f"图床URL请求失败 ({proxy_response.status_code})"
                                        logger.warning(f"[ANALYSIS_SERVICE] {image_type} 图床URL返回{proxy_response.status_code}")
                                else:
                                    load_error = f"图床上传失败: {upload_result}"
                                    logger.warning(f"[ANALYSIS_SERVICE] {image_type} 图床上传失败: {upload_result}")
                            else:
                                load_error = f"本地目录无图片文件: {ref_images_dir}"
                                logger.warning(f"[ANALYSIS_SERVICE] {image_type} 本地目录无图片: {ref_images_dir}")
                        else:
                            load_error = f"本地目录不存在: {ref_images_dir}"
                            logger.warning(f"[ANALYSIS_SERVICE] {image_type} 本地目录不存在: {ref_images_dir}")
                    except Exception as e:
                        load_error = f"本地文件处理异常: {str(e)}"
                        logger.warning(f"[ANALYSIS_SERVICE] {image_type} 本地文件处理异常: {str(e)}")

                if image_bytes:
                    prompt = format_image_analysis_prompt(image_type)
                    result = text_client.generate_text(
                        prompt=prompt,
                        images=[image_bytes],
                        temperature=0.7,
                        max_output_tokens=4000  # 增加到4000以确保完整输出结构化分析
                    )
                    return (image_type, result)
                else:
                    error_msg = load_error or f"未知原因 (URL: {image_url[:50]}...)"
                    logger.warning(f"[ANALYSIS_SERVICE] {image_type} 图片加载失败: {error_msg}")
                    return (image_type, f"[{image_type} 加载失败: {error_msg}]")
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"[ANALYSIS_SERVICE] Failed to analyze {image_type}: {error_msg}")
                return (image_type, f"[{image_type} 分析失败: {error_msg}]")

        # 使用线程池并发分析
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(analyze_image, img_type, img_url)
                for img_type, img_url in images_to_analyze
            ]
            for future in concurrent.futures.as_completed(futures, timeout=90):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"[ANALYSIS_SERVICE] Image analysis future failed: {e}")

        # 合并结果
        if not results:
            return {'description': '', 'error': '所有图片分析均失败'}

        description_parts = []
        cover_results = [r for r in results if r[0] == '封面图']
        content_results = [r for r in results if r[0] == '内容图']

        if cover_results:
            description_parts.append("【封面图分析】")
            for _, desc in cover_results:
                description_parts.append(desc)

        if content_results:
            description_parts.append("\n【内容图整体风格】")
            if len(content_results) == 1:
                description_parts.append(content_results[0][1])
            else:
                description_parts.append("基于选中的 {} 张内容图，整体视觉风格为：\n".format(len(content_results)))
                for _, desc in content_results:
                    description_parts.append(f"- {desc}")

        final_description = "\n".join(description_parts)
        return {'description': final_description}


# 全局单例
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    """获取分析服务单例"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service
