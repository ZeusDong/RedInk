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
            reference_db_path: 已废弃，保留参数兼容性。实际从reference_cache/加载
        """
        # 尝试多个数据源
        self.reference_db: Dict[str, Any] = {}
        self._load_reference_db()

    def _load_reference_db(self):
        """从reference_cache目录加载对标数据"""
        # 尝试的缓存文件路径
        cache_dir = Path(__file__).parent.parent.parent / 'reference_cache'
        cache_files = [
            cache_dir / 'default_cache.json',
            cache_dir / 'xhsKeywordSearch_cache.json'
        ]

        for cache_path in cache_files:
            if cache_path.exists():
                try:
                    self._load_cache_file(cache_path)
                except Exception as e:
                    logger.warning(f"⚠️  加载 {cache_path.name} 失败: {e}")
                    continue

        if self.reference_db:
            logger.info(f"✅ 加载了 {len(self.reference_db)} 条对标记录")
        else:
            logger.warning(f"⚠️  未找到任何缓存数据，搜索功能不可用")

    def _load_cache_file(self, cache_path: Path):
        """
        加载单个缓存文件并转换格式

        缓存格式: {"records": [{"fields": {...}, ...}]}
        目标格式: {record_id: {title, body, industry, metrics, ...}}
        """
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        records = cache_data.get('records', [])
        for record in records:
            try:
                # 转换缓存格式到推荐服务格式
                converted = self._convert_cache_record(record.get('fields', {}))
                if converted and 'record_id' in converted:
                    self.reference_db[converted['record_id']] = converted
            except Exception as e:
                logger.debug(f"跳过无效记录: {e}")
                continue

    def _convert_cache_record(self, fields: Dict) -> Optional[Dict[str, Any]]:
        """将缓存字段转换为推荐服务格式"""
        # 辅助函数：提取字段的text值
        def get_text(field_name: str, default: str = '') -> str:
            field = fields.get(field_name, [])
            if isinstance(field, list) and len(field) > 0:
                item = field[0]
                if isinstance(item, dict):
                    return item.get('text', default)
            return default

        # 辅助函数：提取数值
        def get_int(field_name: str, default: int = 0) -> int:
            value = fields.get(field_name, default)
            if isinstance(value, int):
                return value
            if isinstance(value, list) and len(value) > 0:
                return int(value[0]) if value[0] is not None else default
            return default

        # 提取record_id
        record_id = get_text('record_id')
        if not record_id:
            return None

        # 提取标题
        title = get_text('标题')

        # 提取正文
        body = get_text('正文')

        # 提取封面图
        cover_url = get_text('封面图片链接') or get_text('笔记封面')

        # 提取行业/关键词
        industry = get_text('关键词')

        # 提取互动数据
        likes = get_int('点赞数')
        saves = get_int('收藏数')
        comments = get_int('评论数')
        total_engagement = get_int('总互动量', likes + saves + comments)

        # 提取粉丝数
        follower_count = get_int('博主粉丝数')

        # 计算收藏比
        save_ratio = saves / total_engagement if total_engagement > 0 else 0

        # 提取发布时间
        published_at = fields.get('发布时间', '')

        # 提取笔记类型
        note_type = get_text('笔记类型') or get_text('笔记分类')

        return {
            'record_id': record_id,
            'title': title,
            'body': body,
            'cover_url': cover_url,
            'industry': industry,
            'note_type': note_type,
            'metrics': {
                'likes': likes,
                'saves': saves,
                'comments': comments,
                'total_engagement': total_engagement,
                'save_ratio': save_ratio
            },
            'published_at': published_at,
            'follower_count': follower_count,
            # 保留原始字段用于调试
            '_raw_fields': fields
        }

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
