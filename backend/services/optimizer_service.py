"""
内容优化服务

功能：
- 分析内容并给出优化建议
- 应用优化建议
- 重新计算优化后的评分
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class OptimizerService:
    """内容优化服务"""

    def __init__(self):
        """初始化优化服务"""
        # 规则和阈值配置
        self.scoring_rules = {
            'title': {
                'min_length': 10,
                'max_length': 30,
                'optimal_length': 20,
                'has_emoji_bonus': 2,
                'has_number_bonus': 3
            },
            'structure': {
                'has_intro': 10,
                'has_body': 30,
                'has_conclusion': 10,
                'clear_paragraphs': 20
            },
            'visual': {
                'has_images': 20,
                'good_image_ratio': 10,
                'image_count_optimal': 3
            },
            'engagement': {
                'has_question': 15,
                'has_call_to_action': 20,
                'has_cta': 10,
                'has_emoji_bonus': 5
            }
        }

    def analyze_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析内容并给出优化建议

        Args:
            content: 要分析的内容
                {
                    'title': '标题',
                    'body': '正文',
                    'images': [...],
                    'industry': '行业'
                }

        Returns:
            {
                'score': {...},
                'suggestions': [...]
            }
        """
        title = content.get('title', '')
        body = content.get('body', '')
        images = content.get('images', [])
        industry = content.get('industry', '')

        # 计算各维度分数
        scores = {
            'title': self._score_title(title),
            'structure': self._score_structure(body),
            'visual': self._score_visual(images),
            'engagement': self._score_engagement(body)
        }

        # 总分
        total_score = (
            scores['title'] * 0.25 +
            scores['structure'] * 0.35 +
            scores['visual'] * 0.20 +
            scores['engagement'] * 0.20
        )

        # 生成建议
        suggestions = []

        # 标题建议
        title_issues = self._check_title(title)
        for issue in title_issues:
            suggestions.append({
                'id': f'title_{issue}',
                'type': 'title',
                'severity': issue['severity'],
                'message': issue['message'],
                'detail': issue.get('detail'),
                'action_type': issue.get('action_type', 'edit'),
                'applied': False
            })

        # 结构建议
        structure_issues = self._check_structure(body)
        for issue in structure_issues:
            suggestions.append({
                'id': f'structure_{issue}',
                'type': 'structure',
                'severity': issue['severity'],
                'message': issue['message'],
                'detail': issue.get('detail'),
                'action_type': issue.get('action_type', 'edit'),
                'applied': False
            })

        # 视觉建议
        visual_issues = self._check_visual(images)
        for issue in visual_issues:
            suggestions.append({
                'id': f'visual_{issue}',
                'type': 'visual',
                'severity': issue['severity'],
                'message': issue['message'],
                'detail': issue.get('detail'),
                'action_type': issue.get('action_type', 'edit'),
                'applied': False
            })

        # 互动性建议
        engagement_issues = self._check_engagement(body)
        for issue in engagement_issues:
            suggestions.append({
                'id': f'engagement_{issue}',
                'type': 'engagement',
                'severity': issue['severity'],
                'message': issue['message'],
                'detail': issue.get('detail'),
                'action_type': issue.get('action_type', 'insert'),
                'action_data': issue.get('action_data'),
                'applied': False
            })

        # 按优先级排序
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        suggestions.sort(key=lambda s: severity_order[s['severity']])

        return {
            'score': {
                'total': int(total_score),
                'breakdown': scores
            },
            'suggestions': suggestions
        }

    def _score_title(self, title: str) -> float:
        """评分标题"""
        score = 50  # 基础分

        rules = self.scoring_rules['title']

        # 长度检查
        length = len(title)
        if length < rules['min_length']:
            score -= 10
        elif length > rules['max_length']:
            score -= 15
        elif length == rules['optimal_length']:
            score += 10

        # 是否包含 emoji
        if any(char in title for char in '😀😊😍🎉💕❤️🔥⭐✨'):
            score += rules['has_emoji_bonus']

        # 是否包含数字
        if any(char.isdigit() for char in title):
            score += rules['has_number_bonus']

        return min(max(score, 0), 100)

    def _score_structure(self, body: str) -> float:
        """评分结构"""
        score = 50  # 基础分

        rules = self.scoring_rules['structure']

        # 是否有开头
        if body.strip() and len(body.strip()) > 0:
            score += rules['has_intro']

        # 是否有正文
        if len(body) > 50:
            score += rules['has_body']

        # 是否有结尾
        if body.strip() and body.strip()[-1] in ['。', '！', '～']:
            score += rules['has_conclusion']

        # 段落清晰度（简化检查）
        paragraphs = body.split('\n\n')
        if len(paragraphs) > 1:
            score += rules['clear_paragraphs']

        return min(max(score, 0), 100)

    def _score_visual(self, images: List) -> float:
        """评分视觉"""
        score = 50  # 基础分

        rules = self.scoring_rules['visual']

        # 是否有图片
        if len(images) > 0:
            score += rules['has_images']

        # 图片数量是否合适
        count = len(images)
        if count == rules['image_count_optimal']:
            score += 10
        elif count < 3:
            score -= 10

        # 图片比例（简化）
        if count >= 2:
            score += rules['good_image_ratio']

        return min(max(score, 0), 100)

    def _score_engagement(self, body: str) -> float:
        """评分互动性"""
        score = 50  # 基础分

        rules = self.scoring_rules['engagement']

        # 是否有提问
        if '?' in body or '？' in body:
            score += rules['has_question']

        # 是否有行动号召
        cta_keywords = ['关注', '点赞', '收藏', '分享', '评论', '看看']
        if any(keyword in body for keyword in cta_keywords):
            score += rules['has_cta']

        # 是否有 emoji（额外加分）
        if any(char in body for char in '😀😊😍🎉💕❤️🔥⭐✨💬'):
            score += rules['has_emoji_bonus']

        return min(max(score, 0), 100)

    def _check_title(self, title: str) -> List[Dict[str, Any]]:
        """检查标题问题"""
        issues = []

        if not title or len(title) < 5:
            issues.append({
                'severity': 'critical',
                'message': '标题过短或为空',
                'detail': '建议使用5-30个字符的描述性标题'
            })
        elif len(title) > 30:
            issues.append({
                'severity': 'warning',
                'message': '标题过长',
                'detail': f'当前{len(title)}字符，建议精简到20字左右'
            })

        return issues

    def _check_structure(self, body: str) -> List[Dict[str, Any]]:
        """检查结构问题"""
        issues = []

        # 检查是否是一大段文字
        if '\n' not in body and len(body) > 200:
            issues.append({
                'severity': 'info',
                'message': '内容较长，建议分段',
                'detail': '使用段落和emoji来提高可读性'
            })

        return issues

    def _check_visual(self, images: List) -> List[Dict[str, Any]]:
        """检查视觉问题"""
        issues = []

        if len(images) == 0:
            issues.append({
                'severity': 'warning',
                'message': '建议添加配图',
                'detail': '图文内容配合图片可以获得更好的互动',
                'action_type': 'edit'
            })

        elif len(images) > 6:
            issues.append({
                'severity': 'info',
                'message': '图片数量较多',
                'detail': f'当前{len(images)}张图片，建议精选3-4张最能有效传达信息'
            })

        return issues

    def _check_engagement(self, body: str) -> List[Dict[str, Any]]:
        """检查互动性问题"""
        issues = []

        has_question = '?' in body or '？' in body

        if not has_question:
            issues.append({
                'severity': 'warning',
                'message': '缺少互动引导',
                'detail': '建议在内容结尾添加提问，引导用户评论和分享',
                'action_type': 'insert',
                'action_data': { 'text': '你觉得这个建议怎么样？欢迎在评论区分享你的想法！' }
            })

        # 检查是否有行动号召
        cta_keywords = ['关注', '点赞', '收藏', '分享', '评论']
        has_cta = any(keyword in body for keyword in cta_keywords)

        if not has_cta:
            issues.append({
                'severity': 'info',
                'message': '缺少行动号召',
                'detail': '建议添加明确的行动号召，如"关注了解更多"',
                'action_type': 'insert',
                'action_data': { 'text': '点击关注获取更多精彩内容！' }
            })

        return issues

    def dismiss_suggestion(
        self,
        content: Dict[str, Any],
        suggestion_id: str
    ) -> Dict[str, Any]:
        """
        忽略优化建议

        Args:
            content: 内容对象（包含suggestions列表）
            suggestion_id: 要忽略的建议ID

        Returns:
            更新后的内容（suggestions中标记为已忽略）
        """
        # 获取建议列表
        suggestions = content.get('suggestions', [])

        # 找到目标建议并标记
        for suggestion in suggestions:
            if suggestion.get('id') == suggestion_id:
                suggestion['dismissed'] = True
                logger.info(f"🔕 忽略建议: {suggestion_id}")
                break

        return content

    def apply_suggestion(
        self,
        content: Dict[str, Any],
        suggestion_id: str,
        update_content: bool = True
    ) -> Dict[str, Any]:
        """
        应用优化建议

        Args:
            content: 原始内容
            suggestion_id: 建议ID
            update_content: 是否更新内容

        Returns:
            更新后的内容
        """
        # 模拟实现 - 实际应解析 suggestion_id 并应用相应修改
        suggestion_map = {
            s['id']: s for s in content.get('suggestions', [])
        }

        suggestion = suggestion_map.get(suggestion_id)
        if not suggestion:
            logger.warning(f"⚠️  建议不存在: {suggestion_id}")
            return content

        # 标记为已应用
        suggestion['applied'] = True

        # 应用修改
        updated_content = dict(content)

        if update_content:
            if suggestion['type'] == 'title':
                updated_content['title'] = self._apply_title_suggestion(suggestion)
            elif suggestion['type'] == 'structure':
                updated_content['body'] = self._apply_structure_suggestion(suggestion, content.get('body', ''))
            elif suggestion['type'] == 'engagement':
                updated_content['body'] = self._apply_engagement_suggestion(suggestion, content.get('body', ''))

        # 重新计算分数
        new_score = self.analyze_content(updated_content)

        # 返回更新后的内容和分数
        return {
            **updated_content,
            'new_score': new_score['score'],
            'applied_suggestion': suggestion
        }

    def _apply_title_suggestion(self, suggestion: Any, title: str) -> str:
        """应用标题建议"""
        action = suggestion.get('action_data', {})

        if action.get('text'):
            return f"{title} {action.get('text')}"
        return title

    def _apply_structure_suggestion(self, suggestion: Any, body: str) -> str:
        """应用结构建议"""
        action = suggestion.get('action_data', {})
        text = action.get('text', '')

        if text:
            return f"{body}\n\n{text}"
        return body

    def _apply_engagement_suggestion(self, suggestion: Any, body: str) -> str:
        """应用互动建议"""
        action = suggestion.get('action_data', {})
        text = action.get('text', '')

        if text:
            return f"{body}\n\n{text}"
        return body


# 全局服务实例
_optimizer_service: Optional[OptimizerService] = None


def get_optimizer_service() -> OptimizerService:
    """获取优化服务实例"""
    global _optimizer_service
    if _optimizer_service is None:
        _optimizer_service = OptimizerService()
    return _optimizer_service
