"""
智能推荐服务 V2.0

基于AI分析的笔记推荐系统，只推荐已分析的高质量笔记

主要改进：
- 数据源：从 analysis.db 获取已分析笔记
- 质量控制：只推荐 AI 分析成功的笔记
- AI提炼：提取可学习的结构化元素
- 缓存机制：缓存 AI 提炼结果，提升性能
- 响应增强：推荐理由 + 可学元素 + 匹配等级
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class RecommendationServiceV2:
    """智能推荐服务 V2.0"""

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
            logger.debug("[RECOMMEND] Service already initialized, skipping")
            return
        self._initialized = True

        # 数据库路径
        self.base_dir = Path(__file__).parent.parent.parent
        self.analysis_db_path = self.base_dir / 'analysis' / 'analysis.db'
        self.cache_db_path = self.base_dir / 'analysis' / 'recommendation_cache.db'
        self.synonyms_config_path = self.base_dir / 'synonyms.yaml'

        logger.debug(f"[RECOMMEND] Analysis DB: {self.analysis_db_path}")
        logger.debug(f"[RECOMMEND] Cache DB: {self.cache_db_path}")
        logger.debug(f"[RECOMMEND] Synonyms config: {self.synonyms_config_path}")

        # 确保目录存在
        self.analysis_db_path.parent.mkdir(parents=True, exist_ok=True)

        # 使用线程本地存储连接
        self._local = threading.local()
        self._cache_local = threading.local()

        # 加载同义词配置
        self._synonyms = {}
        self._synonyms_lock = threading.Lock()
        self._load_synonyms_config()

        # 初始化数据库
        self._init_cache_db()

    def _get_analysis_connection(self) -> sqlite3.Connection:
        """获取分析数据库连接"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                str(self.analysis_db_path),
                check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _get_cache_connection(self) -> sqlite3.Connection:
        """获取缓存数据库连接"""
        if not hasattr(self._cache_local, 'conn'):
            self._cache_local.conn = sqlite3.connect(
                str(self.cache_db_path),
                check_same_thread=False
            )
            self._cache_local.conn.row_factory = sqlite3.Row
        return self._cache_local.conn

    def _init_cache_db(self):
        """初始化缓存数据库"""
        conn = self._get_cache_connection()
        cursor = conn.cursor()

        # 创建推荐缓存表
        # 注意：UNIQUE 约束由应用层通过 INSERT OR REPLACE 处理
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendation_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                scenario TEXT,
                record_id TEXT NOT NULL,
                cache_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_rec_cache_topic_scenario
            ON recommendation_cache(topic, scenario)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_rec_cache_record_id
            ON recommendation_cache(record_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_rec_cache_updated_at
            ON recommendation_cache(updated_at)
        ''')

        # Create semantic scores cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_scores_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                record_id TEXT NOT NULL,
                topic_relevance REAL,
                audience_match REAL,
                style_fit REAL,
                performance_bonus REAL,
                final_score REAL,
                scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(topic, record_id)
            )
        ''')

        # Create index for semantic cache
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_semantic_cache_topic_record
            ON semantic_scores_cache(topic, record_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_semantic_cache_scored_at
            ON semantic_scores_cache(scored_at)
        ''')

        conn.commit()
        logger.debug("[RECOMMEND] Cache DB initialized")

    def get_recommendations(
        self,
        topic: str,
        industry: Optional[str] = None,
        scenario: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取推荐列表 V2.0

        Args:
            topic: 搜索主题
            industry: 行业筛选
            scenario: 场景筛选 (beginner|trending|quality)
            limit: 返回数量限制

        Returns:
            推荐结果列表，每个结果包含:
            - record_id, record, match_score (原始关键词匹配分数)
            - final_score (AI语义评分后的最终分数, 0-10)
            - semantic_scores (AI多维度分数, 包含topic_relevance等)
            - match_level (基于final_score的等级)
            - recommend_reasons, learnable_elements
        """
        logger.info(f"[RECOMMEND] topic={topic}, filters=industry:{industry},scenario:{scenario}")

        # 获取已分析的笔记
        analyzed_records = self._get_analyzed_records()
        if not analyzed_records:
            logger.warning("[RECOMMEND] No analyzed records found")
            return []

        # 提取关键词并扩展同义词
        keywords = self._extract_keywords(topic)
        expanded_keywords = self._expand_keywords_with_synonyms(keywords, topic)
        logger.info(f"[RECOMMEND] topic='{topic}', Original: {keywords}, Expanded: {expanded_keywords}")

        # 获取候选记录
        candidates = self._filter_candidates(analyzed_records, industry, scenario)

        if not candidates:
            logger.warning("[RECOMMEND] No candidates after filtering")
            return []

        # 计算每个候选的得分（同时传递原始关键词和扩展关键词）
        scored_results = []
        passed_threshold = 0
        debug_scoring = []  # 用于调试的得分记录

        for record_id, record in candidates.items():
            score_data = self._calculate_score(topic, keywords, expanded_keywords, record)
            title = record.get('title', '')

            # 记录调试信息
            debug_scoring.append({
                'title': title,
                'total': score_data['match_score'],
                'details': score_data['scores']
            })

            # 最低相关性阈值提高到0.3
            if score_data['match_score'] >= 0.3:
                passed_threshold += 1
                # 【新增】确保有推荐洞察（懒加载）
                record = self._ensure_insights(record, topic)

                # 构建结果
                result = {
                    'record_id': record_id,
                    'record': record,
                    'match_score': score_data['match_score'],
                    'match_level': self._calculate_match_level(score_data['match_score']),
                    'recommend_reasons': record.get('recommend_reasons', []),
                    'learnable_elements': record.get('learnable_elements', {})
                }
                scored_results.append(result)

        # 输出调试信息：按得分排序的前10个笔记
        debug_scoring.sort(key=lambda x: x['total'], reverse=True)
        logger.info(f"[RECOMMEND] Top candidates by score:")
        for i, item in enumerate(debug_scoring[:10]):
            logger.info(f"  {i+1}. [{item['total']:.2f}] {item['title'][:40]}...")
        logger.info(f"[RECOMMEND] Passed threshold: {passed_threshold}/{len(candidates)}")

        # 按关键词得分排序，取TOP 30
        scored_results.sort(key=lambda x: x['match_score'], reverse=True)
        top_candidates = scored_results[:30]

        if not top_candidates:
            logger.warning("[RECOMMEND] No candidates after threshold filtering")
            return []

        # 【新增】AI语义评分阶段
        try:
            # 检查缓存
            record_ids = [r['record_id'] for r in top_candidates]
            cached_scores = self._get_semantic_scores_batch(topic, record_ids)

            # 找出未缓存的候选
            uncached_candidates = [
                r for r in top_candidates
                if r['record_id'] not in cached_scores
            ]

            # 调用 AI 评分未缓存的候选
            if uncached_candidates:
                logger.debug(f"[RECOMMEND] AI scoring {len(uncached_candidates)} uncached candidates")
                ai_scores = self._ai_semantic_scoring(topic, uncached_candidates)

                # 保存到缓存
                self._save_semantic_scores_batch(topic, ai_scores)

                # 合并缓存结果
                cached_scores.update(ai_scores)

            # 更新候选的最终得分
            fallback_count = 0
            for result in top_candidates:
                record_id = result['record_id']
                if record_id in cached_scores:
                    semantic_scores = cached_scores[record_id]
                    result['semantic_scores'] = semantic_scores
                    result['final_score'] = semantic_scores['final_score']
                else:
                    # 降级：使用关键词匹配分数（转换为0-10分）
                    result['final_score'] = result['match_score'] * 10
                    result['semantic_scores'] = None
                    fallback_count += 1

            logger.debug(f"[RECOMMEND] AI scored {len(top_candidates) - fallback_count}, fallback {fallback_count}")

            # 按最终得分重新排序
            top_candidates.sort(key=lambda x: x['final_score'], reverse=True)

            # Update match_level based on final_score
            level_counts = {'high': 0, 'medium': 0, 'low': 0}
            for result in top_candidates:
                final_score = result.get('final_score', 0)
                # Convert 0-10 scale to 0-1 for match_level
                normalized_score = final_score / 10
                match_level = self._calculate_match_level(normalized_score)
                result['match_level'] = match_level
                level_counts[match_level] += 1

        except Exception as e:
            # 降级：使用关键词匹配分数
            logger.warning(f"[RECOMMEND] Semantic scoring failed, using keyword match scores: {e}")
            for result in top_candidates:
                result['final_score'] = result['match_score'] * 10
                result['semantic_scores'] = None

        logger.info(f"[RECOMMEND] Returning {min(len(top_candidates), limit)} results (score: {top_candidates[0].get('final_score', 0):.1f} - {top_candidates[-1].get('final_score', 0):.1f})")
        return top_candidates[:limit]

    def recommend_similar(
        self,
        record_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        推荐相似笔记

        Args:
            record_id: 目标笔记ID
            limit: 返回数量限制

        Returns:
            相似推荐列表
        """
        # 获取已分析的笔记
        analyzed_records = self._get_analyzed_records()

        target = analyzed_records.get(record_id)
        if not target:
            logger.warning(f"[RECOMMEND] Record not found: {record_id}")
            return []

        # 基于行业和关键词找相似
        industry = target.get('industry')
        keywords = self._extract_keywords(target.get('title', ''))
        expanded_keywords = self._expand_keywords_with_synonyms(keywords, target.get('title', ''))

        candidates = self._filter_candidates(analyzed_records, industry, None)

        scored = []
        for rid, record in candidates.items():
            if rid == record_id:
                continue

            # 计算相似度（使用扩展关键词）
            similarity = 0.0
            for kw in expanded_keywords[:5]:
                if kw in record.get('title', '').lower():
                    similarity += 0.2

            if similarity > 0:
                match_score = round(min(similarity, 1.0), 2)
                scored.append({
                    'record_id': rid,
                    'record': record,
                    'match_score': match_score,
                    'match_level': self._calculate_match_level(match_score),
                    'recommend_reasons': ['内容相似'],
                    'learnable_elements': {}
                })

        scored.sort(key=lambda x: x['match_score'], reverse=True)
        return scored[:limit]

    def _get_analyzed_records(self) -> Dict[str, Any]:
        """
        从 analysis.db 获取已分析成功的笔记（包含推荐洞察字段）

        Returns:
            {record_id: record_dict} 的字典
        """
        conn = self._get_analysis_connection()
        cursor = conn.cursor()

        try:
            # 检查 analysis_results 表是否存在
            cursor.execute('''
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='analysis_results'
            ''')

            if not cursor.fetchone():
                logger.warning("[RECOMMEND] analysis_results table not found")
                return {}

            # 获取已分析成功的记录（包含推荐洞察字段）
            cursor.execute('''
                SELECT ar.record_id, ar.content, ar.recommend_reasons, ar.learnable_elements,
                       ar.created_at, pn.data
                FROM analysis_results ar
                INNER JOIN pending_notes pn ON ar.record_id = pn.record_id
                WHERE ar.analyzed = 1
                ORDER BY ar.updated_at DESC
            ''')

            rows = cursor.fetchall()
            results = {}

            for row in rows:
                try:
                    record = json.loads(row['data'])
                    # 添加分析内容
                    record['analysis_content'] = row['content']

                    # 兼容处理：cover_image -> cover_url（前端期望 cover_url）
                    if 'cover_image' in record and 'cover_url' not in record:
                        record['cover_url'] = record['cover_image']
                    elif 'cover_url' in record and 'cover_image' not in record:
                        record['cover_image'] = record['cover_url']

                    # 从数据库读取预计算的推荐洞察
                    if row['recommend_reasons']:
                        try:
                            record['recommend_reasons'] = json.loads(row['recommend_reasons'])
                        except (json.JSONDecodeError, TypeError):
                            record['recommend_reasons'] = []
                    else:
                        record['recommend_reasons'] = None  # 标记为缺失，触发懒加载

                    if row['learnable_elements']:
                        try:
                            record['learnable_elements'] = json.loads(row['learnable_elements'])
                        except (json.JSONDecodeError, TypeError):
                            record['learnable_elements'] = {}
                    else:
                        record['learnable_elements'] = None  # 标记为缺失，触发懒加载

                    record['analyzed_at'] = row['created_at']
                    results[row['record_id']] = record
                except (json.JSONDecodeError, KeyError) as e:
                    logger.debug(f"[RECOMMEND] Skipping invalid record: {e}")
                    continue

            logger.debug(f"[RECOMMEND] Loaded {len(results)} analyzed records")
            return results

        except sqlite3.Error as e:
            logger.error(f"[RECOMMEND] Error loading analyzed records: {e}")
            return {}

    def _filter_candidates(
        self,
        records: Dict[str, Any],
        industry: Optional[str],
        scenario: Optional[str]
    ) -> Dict[str, Any]:
        """根据行业和场景筛选候选"""
        initial_count = len(records)
        candidates = dict(records)

        # 行业筛选
        if industry:
            before_industry = len(candidates)
            candidates = {
                k: v for k, v in candidates.items()
                if v.get('industry') == industry
            }

        # 场景筛选
        if scenario == 'beginner':
            # 粉丝友好（小粉丝数 + 高互动）
            before_scenario = len(candidates)
            candidates = {
                k: v for k, v in candidates.items()
                if v.get('follower_count', 0) < 10000 and
                v.get('metrics', {}).get('total_engagement', 0) > 1000
            }
        elif scenario == 'trending':
            # 最近30天发布
            cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            before_scenario = len(candidates)
            candidates = {
                k: v for k, v in candidates.items()
                if v.get('published_at', '') > cutoff
            }
        elif scenario == 'quality':
            # 高收藏比
            before_scenario = len(candidates)
            candidates = {
                k: v for k, v in candidates.items()
                if v.get('metrics', {}).get('save_ratio', 0) > 0.1
            }

        return candidates

    def _calculate_score(
        self,
        topic: str,
        original_keywords: List[str],
        expanded_keywords: List[str],
        record: Dict
    ) -> Dict[str, Any]:
        """
        计算匹配得分

        权重分配（已优化）：
        - 关键词匹配: 60% （必须有搜索词相关内容）
        - 内容相似度: 20%
        - 数据表现: 15%
        - 行业匹配: 5% （仅作为辅助参考）

        Args:
            topic: 用户搜索主题
            original_keywords: 从 topic 提取的原始关键词（2-4字）
            expanded_keywords: 扩展后的关键词（包含同义词）
            record: 笔记记录
        """
        scores = {
            'keyword': 0.0,      # 关键词匹配 (60%)
            'similarity': 0.0,   # 内容相似度 (20%)
            'performance': 0.0,  # 数据表现 (15%)
            'industry': 0.0      # 行业匹配 (5%)
        }

        title = record.get('title', '').lower()
        body = record.get('content', '').lower()

        # 关键词匹配 (60%) - 核心权重
        # 使用 ORIGINAL_KEYWORDS 作为分母，避免同义词稀释得分
        keyword_hits = 0
        effective_keywords = original_keywords if original_keywords else expanded_keywords

        for kw in expanded_keywords:
            if kw in title:
                keyword_hits += 1.5  # 标题命中权重更高
            elif kw in body:
                keyword_hits += 0.8  # 正文中命中权重较低

        if effective_keywords:
            # 限制最高分为 0.6，分母使用原始关键词数量（更少，得分更高）
            scores['keyword'] = min((keyword_hits / len(effective_keywords)) * 0.6, 0.6)

        # 内容相似度 (20%)
        topic_lower = topic.lower()
        if topic_lower in title:
            scores['similarity'] += 0.12  # 完整匹配得分更高
        # 检查部分匹配
        for kw in expanded_keywords:
            if kw in body:
                scores['similarity'] += 0.04
        scores['similarity'] = min(scores['similarity'], 0.2)

        # 数据表现 (15%) - 最多 0.15 分
        metrics = record.get('metrics', {})
        engagement = metrics.get('total_engagement', 0)
        scores['performance'] = min(engagement / 10000 * 0.15, 0.15)

        # 行业匹配 (5%) - 仅作为辅助，不再无条件给分
        # 只有当关键词匹配得分 > 0 时，行业匹配才有效
        if record.get('industry') and scores['keyword'] > 0:
            scores['industry'] = 0.05

        # 总分
        total_score = round(sum(scores.values()), 2)

        return {
            'match_score': total_score,
            'scores': scores
        }

    def _calculate_match_level(self, score: float) -> str:
        """计算匹配等级"""
        if score >= 0.65:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'

    def _get_insights_with_cache(
        self,
        topic: str,
        record: Dict
    ) -> Dict[str, Any]:
        """
        获取或生成AI提炼（带缓存）

        Args:
            topic: 搜索主题
            record: 记录数据

        Returns:
            {recommend_reasons, learnable_elements}
        """
        record_id = record.get('record_id', '')
        scenario = None  # 可以从请求中获取

        # 检查缓存
        cached = self._get_cache(topic, scenario, record_id)
        if cached:
            logger.debug(f"[RECOMMEND] Cache hit for {record_id}")
            return cached

        # 缓存未命中，调用 AI 提炼
        logger.debug(f"[RECOMMEND] Cache miss for {record_id}, calling AI")
        insights = self._ai_extract_insights(topic, record)

        # 保存到缓存
        self._save_cache(topic, scenario, record_id, insights)

        return insights

    def _get_cache(
        self,
        topic: str,
        scenario: Optional[str],
        record_id: str
    ) -> Optional[Dict[str, Any]]:
        """从缓存获取洞察"""
        conn = self._get_cache_connection()
        cursor = conn.cursor()

        try:
            # 检查缓存是否过期（7天）
            cursor.execute('''
                SELECT cache_data, created_at
                FROM recommendation_cache
                WHERE topic = ?
                  AND COALESCE(scenario, '') = ?
                  AND record_id = ?
                  AND datetime(updated_at) > datetime('now', '-7 days')
                ORDER BY updated_at DESC
                LIMIT 1
            ''', (topic, scenario or '', record_id))

            row = cursor.fetchone()
            if row:
                return json.loads(row['cache_data'])

        except sqlite3.Error as e:
            logger.warning(f"[RECOMMEND] Cache read error: {e}")

        return None

    def _save_cache(
        self,
        topic: str,
        scenario: Optional[str],
        record_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """保存洞察到缓存（先删除再插入，确保唯一性）"""
        conn = self._get_cache_connection()
        cursor = conn.cursor()

        try:
            cache_data = json.dumps(data, ensure_ascii=False)
            # 先删除已存在的记录
            cursor.execute('''
                DELETE FROM recommendation_cache
                WHERE topic = ? AND (scenario = ? OR scenario IS NULL) AND record_id = ?
            ''', (topic, scenario, record_id))
            # 再插入新记录
            cursor.execute('''
                INSERT INTO recommendation_cache
                (topic, scenario, record_id, cache_data, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (topic, scenario, record_id, cache_data))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.warning(f"[RECOMMEND] Cache save error: {e}")
            return False

    def _get_semantic_scores_batch(
        self,
        topic: str,
        record_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Batch get semantic scores from cache.

        Args:
            topic: Search topic
            record_ids: List of record IDs to fetch

        Returns:
            Dict mapping record_id to scores dict
        """
        conn = self._get_cache_connection()
        cursor = conn.cursor()

        try:
            # Check cache expiry (7 days)
            cursor.execute('''
                SELECT record_id, topic_relevance, audience_match, style_fit,
                       performance_bonus, final_score
                FROM semantic_scores_cache
                WHERE topic = ?
                  AND record_id IN ({})
                  AND datetime(scored_at) > datetime('now', '-7 days')
            '''.format(','.join(['?'] * len(record_ids))), [topic] + record_ids)

            rows = cursor.fetchall()
            results = {}
            for row in rows:
                results[row['record_id']] = {
                    'topic_relevance': row['topic_relevance'],
                    'audience_match': row['audience_match'],
                    'style_fit': row['style_fit'],
                    'performance_bonus': row['performance_bonus'],
                    'final_score': row['final_score']
                }

            return results

        except sqlite3.Error as e:
            logger.warning(f"[RECOMMEND] Semantic cache read error: {e}")
            return {}

    def _save_semantic_scores_batch(
        self,
        topic: str,
        scores_data: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Batch save semantic scores to cache.

        Args:
            topic: Search topic
            scores_data: Dict mapping record_id to scores dict

        Returns:
            Whether save was successful
        """
        conn = self._get_cache_connection()
        cursor = conn.cursor()

        try:
            for record_id, scores in scores_data.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO semantic_scores_cache
                    (topic, record_id, topic_relevance, audience_match, style_fit,
                     performance_bonus, final_score, scored_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    topic,
                    record_id,
                    scores.get('topic_relevance'),
                    scores.get('audience_match'),
                    scores.get('style_fit'),
                    scores.get('performance_bonus'),
                    scores.get('final_score')
                ))

            conn.commit()
            return True

        except sqlite3.Error as e:
            logger.warning(f"[RECOMMEND] Semantic cache save error: {e}")
            return False

    def _ai_semantic_scoring(
        self,
        topic: str,
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Call AI to batch-score candidates on semantic relevance.

        Args:
            topic: User's search topic
            candidates: List of candidate records

        Returns:
            Dict mapping record_id to scores dict

        Raises:
            Exception: If AI call fails or response parsing fails
        """
        from backend.utils.text_client import get_text_chat_client
        from backend.config import Config
        from backend.prompts.recommendation_prompts import (
            format_semantic_scoring_prompt,
            parse_semantic_scoring_response,
            calculate_final_score
        )

        try:
            # Get text client
            text_config = Config.get_text_provider_config()
            text_client = get_text_chat_client(text_config)

            # Format prompt
            prompt = format_semantic_scoring_prompt(topic, candidates)

            # Call AI with higher timeout for batch processing
            response = text_client.generate_text(
                prompt=prompt,
                temperature=0.3,  # Lower temp for more consistent scoring
                max_output_tokens=4000,
                timeout=45  # Longer timeout for batch scoring
            )

            # Parse response
            scores_by_id = parse_semantic_scoring_response(response)

            # Calculate final scores
            for record_id, scores in scores_by_id.items():
                scores['final_score'] = calculate_final_score(scores)

            logger.info(f"[RECOMMEND] AI scored {len(scores_by_id)} candidates successfully")
            return scores_by_id

        except Exception as e:
            logger.error(f"[RECOMMEND] AI semantic scoring failed: {e}")
            raise  # Re-raise for caller to handle fallback

    def _ensure_insights(
        self,
        record: Dict[str, Any],
        topic: str
    ) -> Dict[str, Any]:
        """
        确保记录有推荐洞察，缺失时懒加载补充

        Args:
            record: 笔记数据字典
            topic: 搜索主题（用于生成推荐理由）

        Returns:
            包含完整推荐洞察的记录
        """
        # 检查是否已有推荐洞察
        has_reasons = bool(record.get('recommend_reasons'))
        has_elements = bool(record.get('learnable_elements'))

        if has_reasons and has_elements:
            # 已有完整数据，直接返回
            return record

        record_id = record.get('record_id', '')
        logger.debug(f"[RECOMMEND] Lazy loading insights for {record_id}")

        try:
            # 调用 AI 生成推荐洞察
            insights = self._ai_extract_insights(topic, record)

            # 更新记录
            if not has_reasons:
                record['recommend_reasons'] = insights.get('recommend_reasons', [])
            if not has_elements:
                record['learnable_elements'] = insights.get('learnable_elements', {})

            # 保存到数据库（下次直接查询）
            self._save_insights_to_db(record_id, insights)

            return record

        except Exception as e:
            logger.warning(f"[RECOMMEND] Failed to lazy load insights for {record_id}: {e}")

            # 降级：使用默认值
            if not has_reasons:
                record['recommend_reasons'] = [
                    f"行业: {record.get('industry', '其他')}",
                    f"互动量: {record.get('metrics', {}).get('total_engagement', 0)}"
                ]
            if not has_elements:
                record['learnable_elements'] = {
                    'hook': '优质开头',
                    'structure': '清晰结构',
                    'tone': '友好风格',
                    'cta': '有效互动'
                }

            return record

    def _save_insights_to_db(
        self,
        record_id: str,
        insights: Dict[str, Any]
    ) -> bool:
        """
        保存推荐洞察到数据库

        Args:
            record_id: 记录ID
            insights: 包含 recommend_reasons 和 learnable_elements 的字典

        Returns:
            是否保存成功
        """
        conn = self._get_analysis_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE analysis_results
                SET recommend_reasons = ?,
                    learnable_elements = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE record_id = ?
            ''', (
                json.dumps(insights.get('recommend_reasons', []), ensure_ascii=False),
                json.dumps(insights.get('learnable_elements', {}), ensure_ascii=False),
                record_id
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logger.warning(f"[RECOMMEND] Failed to save insights to DB: {e}")
            return False

    def _ai_extract_insights(
        self,
        topic: str,
        record: Dict
    ) -> Dict[str, Any]:
        """
        调用AI提炼分析内容

        Args:
            topic: 搜索主题
            record: 记录数据

        Returns:
            {recommend_reasons, learnable_elements}
        """
        from backend.utils.text_client import get_text_chat_client
        from backend.config import Config
        from backend.prompts.recommendation_prompts import (
            format_insights_extraction_prompt,
            parse_insights_response,
            format_semantic_scoring_prompt,
            parse_semantic_scoring_response,
            calculate_final_score
        )

        analysis_content = record.get('analysis_content', '')
        record_id = record.get('record_id', 'unknown')

        if not analysis_content:
            # 没有分析内容，返回默认结果
            logger.warning(f"[RECOMMEND] No analysis_content for {record_id}, using default insights")
            return {
                'recommend_reasons': ['优质内容，值得学习'],
                'learnable_elements': {
                    'hook': '吸引注意',
                    'structure': '清晰结构',
                    'tone': '友好表达',
                    'cta': '互动引导'
                }
            }

        try:
            # 获取文本客户端
            text_config = Config.get_text_provider_config()
            text_client = get_text_chat_client(text_config)

            # 格式化提示词
            prompt = format_insights_extraction_prompt(
                topic=topic,
                analysis_content=analysis_content,
                record=record
            )

            # 调用 AI
            response = text_client.generate_text(
                prompt=prompt,
                temperature=0.5,
                max_output_tokens=2000,
                timeout=30
            )

            # 解析响应
            insights = parse_insights_response(response)
            insights['extracted_at'] = datetime.now().isoformat()

            return insights

        except Exception as e:
            logger.warning(f"[RECOMMEND] AI extraction failed for {record_id}: {e}")

            # 降级策略
            return {
                'recommend_reasons': [
                    f"行业: {record.get('industry', '其他')}",
                    f"互动量: {record.get('metrics', {}).get('total_engagement', 0)}"
                ],
                'learnable_elements': {
                    'hook': '优质开头',
                    'structure': '清晰结构',
                    'tone': '友好风格',
                    'cta': '有效互动'
                },
                'extracted_at': datetime.now().isoformat()
            }

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简单实现）"""
        stopwords = {'的', '了', '是', '在', '有', '和', '与', '等', '一', '个', '怎么', '如何'}

        words = []
        text_lower = text.lower()
        for i in range(len(text_lower)):
            for length in [2, 3, 4]:
                if i + length <= len(text_lower):
                    word = text_lower[i:i+length]
                    if word not in stopwords and word.strip():
                        words.append(word)

        from collections import Counter
        word_count = Counter(words)
        return [w for w, c in word_count.most_common(10)]

    def _expand_keywords_with_synonyms(self, keywords: List[str], topic: str) -> List[str]:
        """
        扩展关键词，使用配置文件 + AI 混合方案

        流程：
        1. 先从 synonyms.yaml 配置文件中查找同义词
        2. 如果配置文件中没有，调用 AI 扩展
        3. AI 扩展结果自动保存到配置文件

        Args:
            keywords: 原始关键词列表
            topic: 用户搜索的主题（用于更精确的匹配）

        Returns:
            扩展后的关键词列表
        """
        expanded_keywords = set(keywords)  # 使用 set 去重

        # 1. 从配置文件中查找
        for kw in keywords:
            if kw in self._synonyms:
                expanded_keywords.update(self._synonyms[kw])

        # 2. 对于新关键词，尝试用 AI 扩展
        new_keywords = [kw for kw in keywords if kw not in self._synonyms]
        if new_keywords:
            ai_synonyms = self._ai_expand_keywords_batch(new_keywords)
            if ai_synonyms:
                # 更新内存中的字典
                self._synonyms.update(ai_synonyms)
                # 保存到配置文件
                self._save_synonyms_config()
                # 合并到结果
                for kw in new_keywords:
                    if kw in ai_synonyms:
                        expanded_keywords.update(ai_synonyms[kw])

        # 3. 对于季节类搜索，额外添加单字匹配（冬、夏、春、秋）
        topic_lower = topic.lower()
        season_chars = ['冬', '夏', '春', '秋']
        for char in season_chars:
            if char in topic_lower:
                expanded_keywords.add(char)
                # 如果单字有同义词，也添加
                if char in self._synonyms:
                    expanded_keywords.update(self._synonyms[char])

        return list(expanded_keywords)

    # ==================== 缓存管理 ====================

    def clear_cache(
        self,
        target: str = 'all',
        record_id: Optional[str] = None,
        older_than_days: int = 7
    ) -> int:
        """
        清除缓存

        Args:
            target: all | expired | record
            record_id: target='record' 时必需
            older_than_days: target='expired' 时，默认7天

        Returns:
            清除的条目数
        """
        conn = self._get_cache_connection()
        cursor = conn.cursor()

        try:
            if target == 'all':
                cursor.execute('DELETE FROM recommendation_cache')
            elif target == 'expired':
                cursor.execute(f'''
                    DELETE FROM recommendation_cache
                    WHERE datetime(updated_at) <= datetime('now', '-{older_than_days} days')
                ''')
            elif target == 'record':
                if not record_id:
                    raise ValueError("record_id required for target='record'")
                cursor.execute('DELETE FROM recommendation_cache WHERE record_id = ?', (record_id,))

            conn.commit()
            cleared = cursor.rowcount
            logger.info(f"[RECOMMEND] Cleared {cleared} cache entries (target={target})")
            return cleared

        except sqlite3.Error as e:
            logger.error(f"[RECOMMEND] Cache clear error: {e}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计

        Returns:
            {total_entries, expired_entries}
        """
        conn = self._get_cache_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT COUNT(*) as total FROM recommendation_cache')
            total = cursor.fetchone()['total']

            cursor.execute('''
                SELECT COUNT(*) as expired
                FROM recommendation_cache
                WHERE datetime(updated_at) <= datetime('now', '-7 days')
            ''')
            expired = cursor.fetchone()['expired']

            return {
                'total_entries': total,
                'expired_entries': expired
            }

        except sqlite3.Error as e:
            logger.error(f"[RECOMMEND] Cache stats error: {e}")
            return {'total_entries': 0, 'expired_entries': 0}

    # ==================== 同义词配置管理 ====================

    def _load_synonyms_config(self):
        """
        加载同义词配置文件
        如果文件不存在，创建空文件
        """
        try:
            if self.synonyms_config_path.exists():
                import yaml
                with open(self.synonyms_config_path, 'r', encoding='utf-8') as f:
                    self._synonyms = yaml.safe_load(f) or {}
                logger.info(f"[RECOMMEND] Loaded synonyms for {len(self._synonyms)} keywords")
            else:
                logger.warning(f"[RECOMMEND] Synonyms config not found at {self.synonyms_config_path}")
                self._synonyms = {}
        except Exception as e:
            logger.error(f"[RECOMMEND] Failed to load synonyms config: {e}")
            self._synonyms = {}

    def _save_synonyms_config(self):
        """
        保存同义词配置到文件
        线程安全，带锁
        """
        try:
            with self._synonyms_lock:
                import yaml
                with open(self.synonyms_config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(
                        self._synonyms,
                        f,
                        allow_unicode=True,
                        sort_keys=True,
                        default_flow_style=False,
                        indent=2
                    )
                logger.info(f"[RECOMMEND] Saved synonyms config with {len(self._synonyms)} keywords")
        except Exception as e:
            logger.error(f"[RECOMMEND] Failed to save synonyms config: {e}")

    def _ai_expand_keywords_batch(self, keywords: List[str]) -> Dict[str, List[str]]:
        """
        批量调用 AI 扩展关键词的同义词

        Args:
            keywords: 需要扩展的关键词列表

        Returns:
            {关键词: [同义词1, 同义词2, ...]}
        """
        if not keywords:
            return {}

        logger.info(f"[RECOMMEND] AI expanding keywords: {keywords}")

        try:
            from backend.utils.text_client import get_text_chat_client
            from backend.config import Config

            text_config = Config.get_text_provider_config()
            text_client = get_text_chat_client(text_config)

            # 构建 Prompt - 严格约束只输出同义词
            prompt = self._build_synonym_expansion_prompt(keywords)

            response = text_client.generate_text(
                prompt=prompt,
                temperature=0.3,  # 低温度，确保输出稳定
                max_output_tokens=2000,
                timeout=30
            )

            # 解析响应
            result = self._parse_synonym_response(response, keywords)
            logger.info(f"[RECOMMEND] AI expanded result: {result}")
            return result

        except Exception as e:
            logger.error(f"[RECOMMEND] AI synonym expansion failed: {e}")
            return {}

    def _build_synonym_expansion_prompt(self, keywords: List[str]) -> str:
        """
        构建同义词扩展的 Prompt，严格约束输出格式
        """
        keywords_str = '\n'.join([f'- {kw}' for kw in keywords])
        return f"""你是一个专业的中文同义词专家。请为以下关键词提供同义词和近义词。

## 要求：
1. 只返回**同义词/近义词**，不要返回反义词、相关词
2. 同义词应该是在搜索时可以互换使用的词
3. 每个关键词返回 3-8 个同义词即可
4. 保持口语化，适合小红书平台

## 需要扩展的关键词：
{keywords_str}

## 输出格式（严格遵守 JSON 格式，不要添加其他文字）：
```json
{{
  "关键词1": ["同义词1", "同义词2", "同义词3"],
  "关键词2": ["同义词1", "同义词2"]
}}
```
"""

    def _parse_synonym_response(self, response: str, original_keywords: List[str]) -> Dict[str, List[str]]:
        """
        解析 AI 的同义词响应
        """
        import re

        try:
            # 尝试提取 JSON
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response.strip()

            import json
            result = json.loads(json_str)

            # 验证结果
            validated = {}
            for kw in original_keywords:
                if kw in result and isinstance(result[kw], list):
                    # 过滤掉空字符串和太长的词
                    synonyms = [s.strip() for s in result[kw] if s.strip() and len(s) <= 10]
                    if synonyms:
                        validated[kw] = synonyms

            return validated

        except Exception as e:
            logger.warning(f"[RECOMMEND] Failed to parse synonym response: {e}")
            return {}


# 全局服务实例
_recommendation_service_v2: Optional[RecommendationServiceV2] = None


def get_recommendation_service_v2() -> RecommendationServiceV2:
    """获取推荐服务 V2 单例"""
    global _recommendation_service_v2
    if _recommendation_service_v2 is None:
        _recommendation_service_v2 = RecommendationServiceV2()
    return _recommendation_service_v2


# 向后兼容：保留旧的服务获取函数
_recommendation_service_v1: Optional['RecommendationService'] = None


def get_recommendation_service():
    """获取推荐服务实例（自动使用V2）"""
    # 导入V1类用于类型检查
    global _recommendation_service_v1

    # 返回V2服务（新的实现）
    return get_recommendation_service_v2()
