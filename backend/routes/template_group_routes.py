"""
模板组 API 路由

提供模板组的 CRUD 操作和技巧管理功能
"""

import logging
from flask import Blueprint, request, jsonify
from backend.services.template_group_service import get_template_group_service

logger = logging.getLogger(__name__)


def create_template_group_blueprint():
    """创建模板组 API 蓝图"""
    bp = Blueprint('template-groups', __name__)

    @bp.route('/template-groups', methods=['POST'])
    def create_template_group():
        """
        创建模板组

        请求体:
        {
          "source_record_id": "原笔记ID",
          "source_title": "原笔记标题",
          "source_industry": "行业",
          "source_cover": "封面图路径",
          "match_score": 0.85,
          "elements": [
            {
              "type": "title|structure|tone|cta",
              "name": "技巧名称",
              "description": "技巧描述",
              "content": "具体技巧内容",
              "examples": ["示例1", "示例2"]
            }
          ]
        }

        响应:
        {
          "success": true,
          "data": {
            "group_id": "uuid"
          }
        }
        """
        try:
            data = request.get_json()

            service = get_template_group_service()
            group = service.create_group(data)

            logger.info(f"📋 创建模板组: {group.get('group_id')}")

            return jsonify({
                'success': True,
                'data': {
                    'group_id': group['group_id']
                }
            })

        except Exception as e:
            logger.error(f"❌ 创建模板组失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/template-groups', methods=['GET'])
    def list_template_groups():
        """
        获取模板组列表

        Query Params:
            type: 技巧类型筛选 (title|structure|tone|cta)
            search: 搜索关键词
            sort_by: 排序字段 (saved_at|usage_count|match_score)

        响应:
        {
          "success": true,
          "data": [...]
        }
        """
        try:
            element_type = request.args.get('type')
            search = request.args.get('search')
            sort_by = request.args.get('sort_by', 'saved_at')

            service = get_template_group_service()
            groups = service.list_groups(
                element_type=element_type,
                search=search,
                sort_by=sort_by
            )

            logger.info(f"📋 模板组列表查询: type={element_type}, search={search}, sort_by={sort_by}, results={len(groups)}")

            return jsonify({
                'success': True,
                'data': groups
            })

        except Exception as e:
            logger.error(f"❌ 模板组列表查询失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/template-groups/<group_id>', methods=['DELETE'])
    def delete_template_group(group_id: str):
        """
        删除模板组

        Args:
            group_id: 模板组ID

        响应:
        {
          "success": true
        }
        """
        try:
            service = get_template_group_service()
            success = service.delete_group(group_id)

            if success:
                logger.info(f"📋 删除模板组: {group_id}")
                return jsonify({
                    'success': True
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '模板组不存在'
                }), 404

        except Exception as e:
            logger.error(f"❌ 删除模板组失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/template-groups/<group_id>/elements/<element_id>', methods=['DELETE'])
    def delete_template_element(group_id: str, element_id: str):
        """
        删除单个技巧

        Args:
            group_id: 模板组ID
            element_id: 技巧ID

        响应:
        {
          "success": true
        }
        """
        try:
            service = get_template_group_service()
            success = service.delete_element(group_id, element_id)

            if success:
                logger.info(f"📋 删除技巧: {element_id} from {group_id}")
                return jsonify({
                    'success': True
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '模板组或技巧不存在'
                }), 404

        except Exception as e:
            logger.error(f"❌ 删除技巧失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/template-groups/<group_id>/elements/<element_id>/apply', methods=['POST'])
    def apply_template_element(group_id: str, element_id: str):
        """
        应用技巧（更新使用次数）

        Args:
            group_id: 模板组ID
            element_id: 技巧ID

        响应:
        {
          "success": true
        }
        """
        try:
            service = get_template_group_service()
            success = service.increment_usage(group_id, element_id)

            if success:
                logger.info(f"📋 应用技巧: {element_id} from {group_id}")
                return jsonify({
                    'success': True
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '模板组或技巧不存在'
                }), 404

        except Exception as e:
            logger.error(f"❌ 应用技巧失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/template-groups/<group_id>', methods=['PUT'])
    def update_template_group(group_id: str):
        """
        更新模板组基本信息

        Args:
            group_id: 模板组ID

        请求体:
        {
          "source_title": "新标题",
          "source_industry": "新行业"
        }

        响应:
        {
          "success": true,
          "data": {...}
        }
        """
        try:
            data = request.get_json()
            service = get_template_group_service()
            group = service.update_group(group_id, data)

            if group:
                logger.info(f"📋 更新模板组: {group_id}")
                return jsonify({
                    'success': True,
                    'data': group
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '模板组不存在'
                }), 404

        except Exception as e:
            logger.error(f"❌ 更新模板组失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/template-groups/<group_id>/elements/<element_id>', methods=['PUT'])
    def update_template_element(group_id: str, element_id: str):
        """
        更新单个技巧

        Args:
            group_id: 模板组ID
            element_id: 技巧ID

        请求体:
        {
          "name": "新名称",
          "description": "新描述",
          "content": "新内容",
          "examples": ["示例1", "示例2"]
        }

        响应:
        {
          "success": true,
          "data": {...}
        }
        """
        try:
            data = request.get_json()
            service = get_template_group_service()
            element = service.update_element(group_id, element_id, data)

            if element:
                logger.info(f"📋 更新技巧: {element_id} from {group_id}")
                return jsonify({
                    'success': True,
                    'data': element
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '模板组或技巧不存在'
                }), 404

        except Exception as e:
            logger.error(f"❌ 更新技巧失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/template-groups/<group_id>/elements', methods=['POST'])
    def add_template_element(group_id: str):
        """
        添加新技巧到分组

        Args:
            group_id: 模板组ID

        请求体:
        {
          "type": "title",
          "name": "新技巧",
          "description": "描述",
          "content": "内容",
          "examples": []
        }

        响应:
        {
          "success": true,
          "data": {...}
        }
        """
        try:
            data = request.get_json()
            service = get_template_group_service()
            element = service.add_element(group_id, data)

            if element:
                logger.info(f"📋 添加新技巧到分组: {group_id}")
                return jsonify({
                    'success': True,
                    'data': element
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '模板组不存在'
                }), 404

        except Exception as e:
            logger.error(f"❌ 添加新技巧失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    logger.debug("✅ Template group routes registered")
    return bp
