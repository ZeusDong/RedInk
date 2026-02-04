"""
对标文案相关 API 路由

包含功能：
- 获取对标文案记录列表（分页、筛选、排序）
- 获取单条记录详情
- 获取统计信息
- 同步飞书数据
- 获取/更新飞书配置
- 测试飞书连接
"""

import logging
from flask import Blueprint, request, jsonify
from backend.config import Config
from backend.services.feishu_service import get_feishu_service

logger = logging.getLogger(__name__)


def create_reference_blueprint():
    """创建对标文案路由蓝图（工厂函数，支持多次调用）"""
    reference_bp = Blueprint('reference', __name__)

    # ==================== 记录查询 ====================

    @reference_bp.route('/reference/records', methods=['GET'])
    def list_records():
        """
        获取对标文案记录列表（分页、筛选、排序）

        查询参数：
        - page: 页码（默认 1）
        - page_size: 每页数量（默认 20）
        - keyword: 搜索关键词（可选）
        - industry: 行业筛选（可选）
        - note_type: 笔记类型筛选（可选）
        - min_likes: 最小点赞数（可选）
        - min_saves: 最小收藏数（可选）
        - sort_by: 排序字段（可选，默认 created_at）
          可选值: created_at, likes, saves, comments, total_engagement, save_ratio
        - sort_order: 排序顺序（可选，默认 desc）
          可选值: asc, desc

        返回：
        - success: 是否成功
        - records: 记录列表
        - total: 总记录数
        - page: 当前页码
        - page_size: 每页数量
        - has_more: 是否有更多数据

        示例请求：
        GET /api/reference/records?page=1&page_size=20&industry=美食&sort_by=likes&sort_order=desc
        """
        try:
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 20))
            keyword = request.args.get('keyword')
            industry = request.args.get('industry')
            note_type = request.args.get('note_type')
            min_likes = request.args.get('min_likes')
            min_saves = request.args.get('min_saves')
            sort_by = request.args.get('sort_by', 'created_at')
            sort_order = request.args.get('sort_order', 'desc')

            # Parse numeric parameters
            if min_likes is not None:
                min_likes = int(min_likes)
            if min_saves is not None:
                min_saves = int(min_saves)

            # Get workspace configuration
            workspace_name = Config.get_active_feishu_workspace()
            workspace_config = Config.get_feishu_workspace_config(workspace_name)

            # Configure service
            service = get_feishu_service()
            service.configure(workspace_name, workspace_config)

            # Query records
            result = service.list_records(
                page=page,
                page_size=page_size,
                keyword=keyword,
                industry=industry,
                note_type=note_type,
                min_likes=min_likes,
                min_saves=min_saves,
                sort_by=sort_by,
                sort_order=sort_order
            )

            return jsonify({
                "success": True,
                "records": [r.to_dict() for r in result.records],
                "total": result.total,
                "page": result.page,
                "page_size": result.page_size,
                "has_more": result.has_more
            }), 200

        except ValueError as e:
            error_msg = str(e)
            return jsonify({
                "success": False,
                "error": f"参数错误。\n错误详情: {error_msg}"
            }), 400
        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取对标文案列表失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"获取对标文案列表失败。\n错误详情: {error_msg}"
            }), 500

    @reference_bp.route('/reference/records/<record_id>', methods=['GET'])
    def get_record(record_id):
        """
        获取单条对标文案记录详情

        路径参数：
        - record_id: 记录 ID

        返回：
        - success: 是否成功
        - record: 完整的记录数据
        """
        try:
            # Get workspace configuration
            workspace_name = Config.get_active_feishu_workspace()
            workspace_config = Config.get_feishu_workspace_config(workspace_name)

            # Configure service
            service = get_feishu_service()
            service.configure(workspace_name, workspace_config)

            record = service.get_record(record_id)

            if not record:
                return jsonify({
                    "success": False,
                    "error": f"对标文案记录不存在：{record_id}"
                }), 404

            return jsonify({
                "success": True,
                "record": record.to_dict()
            }), 200

        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取对标文案详情失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"获取对标文案详情失败。\n错误详情: {error_msg}"
            }), 500

    # ==================== 统计信息 ====================

    @reference_bp.route('/reference/stats', methods=['GET'])
    def get_stats():
        """
        获取对标文案统计信息

        返回：
        - success: 是否成功
        - total_records: 总记录数
        - industry_distribution: 行业分布
        - note_type_distribution: 笔记类型分布
        - avg_likes: 平均点赞数
        - avg_saves: 平均收藏数
        - avg_comments: 平均评论数
        """
        try:
            # Get workspace configuration
            workspace_name = Config.get_active_feishu_workspace()
            workspace_config = Config.get_feishu_workspace_config(workspace_name)

            # Configure service
            service = get_feishu_service()
            service.configure(workspace_name, workspace_config)

            stats = service.get_statistics()

            return jsonify({
                "success": True,
                "total_records": stats.total_records,
                "industry_distribution": stats.industry_distribution,
                "note_type_distribution": stats.note_type_distribution,
                "avg_likes": stats.avg_likes,
                "avg_saves": stats.avg_saves,
                "avg_comments": stats.avg_comments
            }), 200

        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取统计信息失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"获取统计信息失败。\n错误详情: {error_msg}"
            }), 500

    # ==================== 数据同步 ====================

    @reference_bp.route('/reference/sync', methods=['POST'])
    def sync_data():
        """
        同步飞书数据（清除缓存并重新获取）

        返回：
        - success: 是否成功
        - message: 同步结果消息
        - count: 同步的记录数
        - synced_at: 同步时间
        """
        try:
            # Get workspace configuration
            workspace_name = Config.get_active_feishu_workspace()
            workspace_config = Config.get_feishu_workspace_config(workspace_name)

            # Configure service
            service = get_feishu_service()
            service.configure(workspace_name, workspace_config)

            result = service.sync_data()

            return jsonify({
                "success": True,
                "message": result.get("message", "同步成功"),
                "count": result.get("count", 0),
                "synced_at": result.get("synced_at")
            }), 200

        except Exception as e:
            error_msg = str(e)
            logger.error(f"同步数据失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"同步数据失败。\n错误详情: {error_msg}"
            }), 500

    # ==================== 配置管理 ====================

    @reference_bp.route('/reference/config', methods=['GET'])
    def get_config():
        """
        获取飞书配置（隐藏敏感信息）

        返回：
        - success: 是否成功
        - config: 飞书配置（敏感字段已脱敏）
        """
        try:
            config = Config.load_feishu_providers_config()

            # 脱敏处理
            safe_config = {
                "active_workspace": config.get("active_workspace", "default"),
                "workspaces": {}
            }

            for name, workspace in config.get("workspaces", {}).items():
                safe_config["workspaces"][name] = {
                    "name": workspace.get("name", ""),
                    "app_id": workspace.get("app_id", ""),
                    "app_secret": "***" if workspace.get("app_secret") else "",
                    "base_url": workspace.get("base_url", ""),
                    "user_access_token": "***" if workspace.get("user_access_token") else "",
                    "cache_enabled": workspace.get("cache_enabled", True),
                    "cache_ttl": workspace.get("cache_ttl", 3600),
                }

            return jsonify({
                "success": True,
                "config": safe_config
            }), 200

        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取飞书配置失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"获取飞书配置失败。\n错误详情: {error_msg}"
            }), 500

    @reference_bp.route('/reference/config', methods=['POST'])
    def update_config():
        """
        更新飞书配置

        请求体：
        - active_workspace: 激活的工作区名称
        - workspaces: 工作区配置字典

        返回：
        - success: 是否成功
        - message: 结果消息
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    "success": False,
                    "error": "参数错误：请求体不能为空。"
                }), 400

            # Validate required fields
            if "workspaces" not in data:
                return jsonify({
                    "success": False,
                    "error": "参数错误：workspaces 字段不能为空。"
                }), 400

            # Save configuration
            Config.save_feishu_providers_config(data)

            return jsonify({
                "success": True,
                "message": "飞书配置已保存"
            }), 200

        except Exception as e:
            error_msg = str(e)
            logger.error(f"更新飞书配置失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"更新飞书配置失败。\n错误详情: {error_msg}"
            }), 500

    @reference_bp.route('/reference/config/test', methods=['POST'])
    def test_connection():
        """
        测试飞书连接

        请求体：
        - app_id: 应用 ID
        - app_secret: 应用密钥
        - user_access_token: 用户访问令牌（可选）
        - base_url: 多维表格 URL

        返回：
        - success: 是否成功
        - message: 测试结果消息
        - tables: 找到的数据表列表（如果提供了 user_access_token）
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    "success": False,
                    "error": "参数错误：请求体不能为空。"
                }), 400

            app_id = data.get('app_id')
            app_secret = data.get('app_secret')
            user_access_token = data.get('user_access_token', '')
            base_url = data.get('base_url')

            if not app_id or not app_secret or not base_url:
                return jsonify({
                    "success": False,
                    "error": "参数错误：app_id、app_secret 和 base_url 不能为空。"
                }), 400

            # Test connection
            service = get_feishu_service()
            result = service.test_connection({
                "app_id": app_id,
                "app_secret": app_secret,
                "user_access_token": user_access_token,
                "base_url": base_url,
            })

            if result.get("success"):
                return jsonify({
                    "success": True,
                    "message": result.get("message", "连接成功"),
                    "tables": result.get("tables", []),
                    "app_token": result.get("app_token", "")
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result.get("error", "连接失败")
                }), 400

        except Exception as e:
            error_msg = str(e)
            logger.error(f"测试飞书连接失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"测试飞书连接失败。\n错误详情: {error_msg}"
            }), 500

    return reference_bp
