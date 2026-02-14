"""
推荐服务 - 基于主题推荐相关的对标笔记

功能：
- 根据主题关键词推荐相关对标笔记
- 支持场景筛选（新手入门、追热点、提升质量）
- 多维度打分（行业匹配、关键词匹配、数据表现、内容相似度）
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class RecommendationService:
    """推荐服务"""

    def __init__(self, reference_db_path: Optional[str] = None):
        """
        初始化推荐服务

        Args:
            reference_db_path: 对标数据库路径，默认使用 data/reference.json
        """
        if reference_db_path is None:
            # 默认对标数据路径
            reference_db_path = Path(__file__).parent.parent.parent / 'data' / 'reference.json'

        self.reference_db_path = Path(reference_db_path)
        self.reference_db: Dict[str, Any] = {}
        self._load_reference_db()

    def _load_reference_db(self):
        """加载对标数据"""
        try:
            if self.reference_db_path.exists():
                with open(self.reference_db_path, 'r', encoding='utf-8') as f:
                    self.reference_db = json.load(f)
                logger.info(f"✅ 加载了 {len(self.reference_db)} 条对标记录")
            else:
                logger.warning(f"⚠️  对标数据文件不存在: {self.reference_db_path}")
                self.reference_db = {}
        except Exception as e:
            logger.error(f"❌ 加载对标数据失败: {e}")
            self.reference_db = {}

    def get_recommendations(
        self,
        topic: str,
        industry: Optional[str] = None,
        scenario: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取推荐列表

        Args:
            topic: 搜索主题
            industry: 行业筛选
            scenario: 场景筛选 (beginner/trending/quality)
            limit: 返回数量限制

        Returns:
            推荐结果列表
        """
        # 提取关键词
        keywords = self._extract_keywords(topic)

        # 获取候选记录
        candidates = self._get_candidates(industry, scenario)

        # 计算每个候选的得分
        scored_results = []
        for record_id, record in candidates.items():
            score_data = self._calculate_score(topic, keywords, record, scenario)
            if score_data['match_score'] > 0.1:  # 最低相关性阈值
                scored_results.append(score_data)

        # 按得分排序
        scored_results.sort(key=lambda x: x['match_score'], reverse=True)

        return scored_results[:limit]

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
        target = self.reference_db.get(record_id)
        if not target:
            logger.warning(f"⚠️  找不到记录: {record_id}")
            return []

        # 简化实现：基于行业和关键词
        industry = target.get('industry')
        keywords = self._extract_keywords(target.get('title', ''))

        candidates = self._get_candidates(industry, None)

        scored = []
        for rid, record in candidates.items():
            if rid == record_id:
                continue

            # 计算相似度
            similarity = 0.0
            for kw in keywords[:5]:  # 只用前5个关键词
                if kw in record.get('title', '').lower():
                    similarity += 0.2

            if similarity > 0:
                scored.append({
                    'record_id': rid,
                    'record': record,
                    'match_score': round(min(similarity, 1.0), 2),
                    'reasons': ['similarity']
                })

        scored.sort(key=lambda x: x['match_score'], reverse=True)
        return scored[:limit]

    def _get_candidates(
        self,
        industry: Optional[str],
        scenario: Optional[str]
    ) -> Dict[str, Any]:
        """获取候选记录"""
        candidates = dict(self.reference_db)

        # 行业筛选
        if industry:
            candidates = {
                k: v for k, v in candidates.items()
                if v.get('industry') == industry
            }

        # 场景筛选
        if scenario == 'beginner':
            # 粉丝友好（小粉丝数 + 高互动）
            candidates = {
                k: v for k, v in candidates.items()
                if v.get('follower_count', 0) < 10000 and
                v.get('metrics', {}).get('total_engagement', 0) > 1000
            }
        elif scenario == 'trending':
            # 最近30天发布
            from datetime import datetime, timedelta
            cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            candidates = {
                k: v for k, v in candidates.items()
                if v.get('published_at', '') > cutoff
            }
        elif scenario == 'quality':
            # 高收藏比
            candidates = {
                k: v for k, v in candidates.items()
                if v.get('metrics', {}).get('save_ratio', 0) > 0.1
            }

        return candidates

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简单实现，可升级为 NLP）"""
        # 停用词
        stopwords = {'的', '了', '是', '在', '有', '和', '与', '等', '一', '个', '怎么', '如何'}

        # 简单分词（按2-4字切分）
        words = []
        text_lower = text.lower()
        for i in range(len(text_lower)):
            for length in [2, 3, 4]:
                if i + length <= len(text_lower):
                    word = text_lower[i:i+length]
                    if word not in stopwords and word.strip():
                        words.append(word)

        # 统计词频
        from collections import Counter
        word_count = Counter(words)

        # 返回前10个高频词
        return [w for w, c in word_count.most_common(10)]

    def _calculate_score(
        self,
        topic: str,
        keywords: List[str],
        record: Dict,
        scenario: Optional[str]
    ) -> Dict[str, Any]:
        """计算推荐得分"""
        scores = {
            'industry': 0.0,
            'keyword': 0.0,
            'performance': 0.0,
            'similarity': 0.0
        }
        reasons = []

        # 行业匹配 (30%)
        if record.get('industry'):
            scores['industry'] = 0.3
            reasons.append('industry')

        # 关键词匹配 (30%)
        title = record.get('title', '').lower()
        body = record.get('body', '').lower()
        keyword_hits = 0
        for kw in keywords:
            if kw in title or kw in body:
                keyword_hits += 1
        if keywords:
            scores['keyword'] = min((keyword_hits / len(keywords)) * 0.3, 0.3)
        if keyword_hits > 0:
            reasons.append('keyword')

        # 数据表现 (20%)
        metrics = record.get('metrics', {})
        engagement = metrics.get('total_engagement', 0)
        # 归一化：假设10000互动为满分
        scores['performance'] = min(engagement / 10000 * 0.2, 0.2)
        if engagement > 5000:
            reasons.append('trending')

        # 内容相似度 (20%) - 简化实现
        topic_lower = topic.lower()
        similarity = 0.0
        if topic_lower in title:
            similarity += 0.1
        if any(kw in body for kw in keywords):
            similarity += 0.1
        scores['similarity'] = similarity

        # 总分
        total_score = sum(scores.values())

        return {
            'record_id': record.get('record_id', ''),
            'record': record,
            'match_score': round(total_score, 2),
            'reasons': reasons,
            'scores': scores
        }


# 全局服务实例
_recommendation_service: Optional[RecommendationService] = None


def get_recommendation_service() -> RecommendationService:
    """获取推荐服务实例"""
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service
