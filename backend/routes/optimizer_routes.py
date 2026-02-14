"""
内容优化API路由

提供内容分析和优化建议功能
"""

import logging
from flask import Blueprint, request, jsonify
from backend.services.optimizer_service import get_optimizer_service

logger = logging.getLogger(__name__)


def create_optimizer_blueprint():
    """创建优化API蓝图"""
    bp = Blueprint('optimizer', __name__)

    @bp.route('/optimize/analyze', methods=['POST'])
    def analyze_content():
        """
        分析内容并给出优化建议

        请求体:
        {
            "content": {
                "title": "...",
                "body": "...",
                "images": [...],
                "industry": "美妆护肤"
            }
        }

        Returns:
        {
            "success": true,
            "data": {
                "score": {...},
                "suggestions": [...]
            }
        }
        """
        try:
            data = request.get_json()
            content = data.get('content', {})

            service = get_optimizer_service()
            result = service.analyze_content(content)

            logger.info(f"🔍 内容分析: title={content.get('title', '')}")

            return jsonify({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f"❌ 内容分析失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/optimize/apply', methods=['POST'])
    def apply_suggestion():
        """
        应用优化建议

        请求体:
        {
            "content": {...},           # 新增：原始内容
            "suggestion_id": "...",
            "action_type": "edit",
            "action_data": {...}
        }

        Returns:
        {
            "success": true,
            "data": {
                "updated_content": {...},
                "new_score": {...}
            }
        }
        """
        try:
            data = request.get_json()
            content = data.get('content', {})       # 新增
            suggestion_id = data.get('suggestion_id')

            service = get_optimizer_service()
            result = service.apply_suggestion(
                content=content,                    # 新增必需参数
                suggestion_id=suggestion_id,
                update_content=True
            )

            logger.info(f"✅ 应用建议: {suggestion_id}")

            return jsonify({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f"❌ 应用建议失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/optimize/dismiss', methods=['POST'])
    def dismiss_suggestion():
        """
        忽略优化建议

        请求体:
        {
            "content": {...},           # 新增：原始内容
            "suggestion_id": "..."
        }

        Returns:
        {
            "success": true
        }
        """
        try:
            data = request.get_json()
            content = data.get('content', {})       # 新增
            suggestion_id = data.get('suggestion_id')

            service = get_optimizer_service()
            service.dismiss_suggestion(
                content=content,                    # 新增必需参数
                suggestion_id=suggestion_id
            )

            logger.info(f"🔕 忽略建议: {suggestion_id}")

            return jsonify({
                'success': True
            })

        except Exception as e:
            logger.error(f"❌ 忽略建议失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    logger.debug("✅ Optimizer routes registered")
    return bp
