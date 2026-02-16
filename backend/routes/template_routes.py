"""
模板API路由

提供模板的CRUD操作和应用功能
"""

import logging
from flask import Blueprint, request, jsonify
from backend.services.template_service import get_template_service

logger = logging.getLogger(__name__)


def create_template_blueprint():
    """创建模板API蓝图"""
    bp = Blueprint('templates', __name__)

    @bp.route('/templates', methods=['GET'])
    def list_templates():
        """
        获取模板列表

        Query Params:
            type: 模板类型筛选 (title/structure/visual)
            industry: 行业筛选

        Returns:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            template_type = request.args.get('type')
            industry = request.args.get('industry')

            service = get_template_service()
            templates = service.list_templates(
                template_type=template_type,
                industry=industry
            )

            logger.info(f"📋 模板列表查询: type={template_type}, industry={industry}, results={len(templates)}")

            return jsonify({
                'success': True,
                'data': templates
            })

        except Exception as e:
            logger.error(f"❌ 模板列表查询失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/templates', methods=['POST'])
    def create_template():
        """
        创建新模板

        请求体:
        {
            "type": "title",
            "name": "吸引眼球的标题公式",
            "industry": "美妆护肤",
            "pattern": "{主题}的{数字}个秘密，让你惊艳{季节}",
            "variables": ["{主题}", "{数字}", "{季节}"],
            "description": "通过数字和季节增强标题吸引力",
            "examples": ["示例1", "示例2"],
            "source_records": []
        }

        Returns:
        {
            "success": true,
            "data": {...}
        }
        """
        try:
            data = request.get_json()

            service = get_template_service()
            template = service.create_template(data)

            logger.info(f"📋 创建模板: {template.get('id')}")

            return jsonify({
                'success': True,
                'data': template
            })

        except Exception as e:
            logger.error(f"❌ 创建模板失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/templates/<template_id>', methods=['GET'])
    def get_template(template_id: str):
        """
        获取模板详情

        Args:
            template_id: 模板ID

        Returns:
        {
            "success": true,
            "data": {...}
        }
        """
        try:
            service = get_template_service()
            template = service.get_template(template_id)

            if template:
                return jsonify({
                    'success': True,
                    'data': template
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '模板不存在'
                }), 404

        except Exception as e:
            logger.error(f"❌ 获取模板失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/templates/apply', methods=['POST'])
    def apply_template():
        """
        应用模板生成内容

        请求体:
        {
            "template_id": "xxx",
            "context": {
                "topic": "春季护肤",
                "industry": "美妆护肤"
            }
        }

        Returns:
        {
            "success": true,
            "data": {
                "title": "...",
                "outline": {...},
                "visual_guide": {...}
            }
        }
        """
        try:
            data = request.get_json()
            template_id = data.get('template_id')
            context = data.get('context', {})

            service = get_template_service()
            result = service.apply_template(template_id, context)

            logger.info(f"📋 应用模板: {template_id}")

            return jsonify({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f"❌ 应用模板失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/templates/<template_id>', methods=['DELETE'])
    def delete_template(template_id: str):
        """
        删除模板

        Args:
            template_id: 模板ID

        Returns:
        {
            "success": true
        }
        """
        try:
            service = get_template_service()
            success = service.delete_template(template_id)

            if success:
                logger.info(f"📋 删除模板: {template_id}")
                return jsonify({
                    'success': True
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '删除失败'
                }), 400

        except Exception as e:
            logger.error(f"❌ 删除模板失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/templates/extract', methods=['POST'])
    def extract_template():
        """
        从历史记录中提取模板元素

        请求体:
        {
            "record_id": "xxx"
        }

        Returns:
        {
            "success": true,
            "data": {
                "suggested_name": "护肤亲切闺蜜风模板",
                "title_template": "...",
                "structure_template": "...",
                "tone_style": "...",
                "cta_type": "...",
                "elements": [...]
            }
        }
        """
        try:
            data = request.get_json()
            record_id = data.get('record_id')

            if not record_id:
                return jsonify({
                    'success': False,
                    'error': '缺少 record_id'
                }), 400

            service = get_template_service()
            template_data = service.extract_template_from_record(record_id)

            logger.info(f"📋 提取模板: record_id={record_id}")

            return jsonify({
                'success': True,
                'data': template_data
            })

        except Exception as e:
            logger.error(f"❌ 提取模板失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    logger.debug("✅ Template routes registered")
    return bp
