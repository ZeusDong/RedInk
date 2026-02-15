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
from flask import Blueprint, request, jsonify, Response
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

            # Add workspace parameter support (default to active workspace)
            workspace_name = request.args.get('workspace')
            if not workspace_name:
                workspace_name = Config.get_active_feishu_workspace()

            workspace_config = Config.get_feishu_workspace_config(workspace_name)

            # Configure service
            service = get_feishu_service()
            service.configure(workspace_name, workspace_config)

            # Query records
            logger.info(f"Querying records with params: page={page}, page_size={page_size}, keyword={keyword}")
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

            logger.info(f"Query result: {len(result.records)} records, total={result.total}")
            records_dict = [r.to_dict() for r in result.records]

            response_data = {
                "success": True,
                "records": records_dict,
                "total": result.total,
                "page": result.page,
                "page_size": result.page_size,
                "has_more": result.has_more
            }

            return jsonify(response_data), 200

        except ValueError as e:
            error_msg = str(e)
            # Check if this is a token refresh error requiring re-auth
            if "refresh_token" in error_msg or "重新授权" in error_msg:
                return jsonify({
                    "success": False,
                    "error": error_msg,
                    "requires_reauth": True
                }), 403  # Forbidden - requires re-authorization
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
            # Get all available workspace names
            feishu_config = Config.load_feishu_providers_config()
            all_workspace_names = list(feishu_config.get('workspaces', {}).keys())

            # Start with the requested or active workspace
            workspace_name = request.args.get('workspace')
            if not workspace_name:
                workspace_name = Config.get_active_feishu_workspace()

            # Create ordered list: try requested/active first, then others
            workspaces_to_try = [workspace_name]
            for ws in all_workspace_names:
                if ws != workspace_name:
                    workspaces_to_try.append(ws)

            logger.info(f"[REFERENCE] Trying to find record {record_id} in workspaces: {workspaces_to_try}")

            # Try each workspace in order
            service = get_feishu_service()
            record = None
            found_workspace = None

            for ws_name in workspaces_to_try:
                try:
                    workspace_config = Config.get_feishu_workspace_config(ws_name)
                    service.configure(ws_name, workspace_config)
                    record = service.get_record(record_id)
                    if record:
                        found_workspace = ws_name
                        logger.info(f"[REFERENCE] Found record {record_id} in workspace: {ws_name}")
                        break
                except Exception as ws_error:
                    logger.warning(f"[REFERENCE] Failed to fetch from workspace {ws_name}: {ws_error}")
                    continue

            if not record:
                return jsonify({
                    "success": False,
                    "error": f"对标文案记录不存在：{record_id} (tried workspaces: {workspaces_to_try})"
                }), 404

            return jsonify({
                "success": True,
                "record": record.to_dict()
            }), 200

        except ValueError as e:
            error_msg = str(e)
            # Check if this is a token refresh error requiring re-auth
            if "refresh_token" in error_msg or "重新授权" in error_msg:
                return jsonify({
                    "success": False,
                    "error": error_msg,
                    "requires_reauth": True
                }), 403  # Forbidden - requires re-authorization
            return jsonify({
                "success": False,
                "error": f"参数错误。\n错误详情: {error_msg}"
            }), 400
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

            logger.info(f"Statistics: total_records={stats.total_records}, industries={len(stats.industry_distribution)}")

            return jsonify({
                "success": True,
                "total_records": stats.total_records,
                "industry_distribution": stats.industry_distribution,
                "note_type_distribution": stats.note_type_distribution,
                "avg_likes": stats.avg_likes,
                "avg_saves": stats.avg_saves,
                "avg_comments": stats.avg_comments
            }), 200

        except ValueError as e:
            error_msg = str(e)
            # Check if this is a token refresh error requiring re-auth
            if "refresh_token" in error_msg or "重新授权" in error_msg:
                return jsonify({
                    "success": False,
                    "error": error_msg,
                    "requires_reauth": True
                }), 403  # Forbidden - requires re-authorization
            return jsonify({
                "success": False,
                "error": f"参数错误。\n错误详情: {error_msg}"
            }), 400
        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取统计信息失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"获取统计信息失败。\n错误详情: {error_msg}"
            }), 500

    @reference_bp.route('/reference/counts', methods=['GET'])
    def get_workspace_counts():
        """
        Get record counts from cache files (very fast, no API calls)

        This reads directly from the cached JSON files to get totals,
        avoiding expensive Feishu API calls just for counting.
        """
        try:
            import os
            import json
            cache_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'reference_cache')

            counts = {}
            if os.path.exists(cache_dir):
                for filename in os.listdir(cache_dir):
                    if filename.endswith('_cache.json'):
                        cache_path = os.path.join(cache_dir, filename)
                        try:
                            with open(cache_path, 'r', encoding='utf-8') as f:
                                cache_data = json.load(f)
                                workspace = cache_data.get('workspace', filename.replace('_cache.json', ''))
                                counts[workspace] = cache_data.get('total', 0)
                        except Exception as e:
                            logger.warning(f"Failed to read cache file {filename}: {e}")

            return jsonify({
                "success": True,
                "counts": counts
            }), 200

        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取工作区计数失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"获取工作区计数失败。\n错误详情: {error_msg}"
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

        except ValueError as e:
            error_msg = str(e)
            # Check if this is a token refresh error requiring re-auth
            if "refresh_token" in error_msg or "重新授权" in error_msg:
                return jsonify({
                    "success": False,
                    "error": error_msg,
                    "requires_reauth": True
                }), 403  # Forbidden - requires re-authorization
            return jsonify({
                "success": False,
                "error": f"参数错误。\n错误详情: {error_msg}"
            }), 400
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

        支持两种配置格式：
        1. 新格式：全局 OAuth + 工作区特定配置
        2. 旧格式：每个工作区包含完整配置（向后兼容）

        返回：
        - success: 是否成功
        - config: 飞书配置（敏感字段已脱敏）
        """
        try:
            config = Config.load_feishu_providers_config()

            # Check for new format (global oauth section)
            has_global_oauth = 'oauth' in config

            # 脱敏处理
            safe_config = {
                "active_workspace": config.get("active_workspace", "default"),
                "workspaces": {}
            }

            # Add global OAuth section if present (new format)
            if has_global_oauth:
                oauth = config.get("oauth", {})
                safe_config["oauth"] = {
                    "app_id": oauth.get("app_id", ""),
                    "app_secret": "***" if oauth.get("app_secret") else "",
                    "user_access_token": "***" if oauth.get("user_access_token") else "",
                    "refresh_token": "***" if oauth.get("refresh_token") else "",
                    "token_expires_at": oauth.get("token_expires_at", ""),
                    "refresh_token_expires_at": oauth.get("refresh_token_expires_at", ""),
                }

            for name, workspace in config.get("workspaces", {}).items():
                safe_config["workspaces"][name] = {
                    "name": workspace.get("name", ""),
                    "base_url": workspace.get("base_url", ""),
                    "cache_enabled": workspace.get("cache_enabled", True),
                    "cache_ttl": workspace.get("cache_ttl", 3600),
                }

                # For old format (no global oauth), include oauth fields in workspace
                if not has_global_oauth:
                    safe_config["workspaces"][name].update({
                        "app_id": workspace.get("app_id", ""),
                        "app_secret": "***" if workspace.get("app_secret") else "",
                        "user_access_token": "***" if workspace.get("user_access_token") else "",
                        "refresh_token": "***" if workspace.get("refresh_token") else "",
                        "token_expires_at": workspace.get("token_expires_at", ""),
                        "refresh_token_expires_at": workspace.get("refresh_token_expires_at", ""),
                    })

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

        支持两种配置格式：
        1. 新格式：全局 OAuth + 工作区特定配置
        2. 旧格式：每个工作区包含完整配置（向后兼容）

        请求体：
        - active_workspace: 激活的工作区名称
        - oauth: (可选) 全局 OAuth 配置（新格式）
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

            # Load existing config to preserve secret values
            existing_config = Config.load_feishu_providers_config()

            # Handle global OAuth section (new format)
            if 'oauth' in data:
                existing_oauth = existing_config.get('oauth', {})
                oauth_fields = ['app_id', 'app_secret', 'user_access_token', 'refresh_token',
                              'token_expires_at', 'refresh_token_expires_at']

                for field in oauth_fields:
                    incoming_value = data['oauth'].get(field)
                    # Preserve existing value if masked or empty
                    if incoming_value == '***' or incoming_value == '':
                        if field in existing_oauth:
                            data['oauth'][field] = existing_oauth[field]

            # Handle workspace config
            existing_workspaces = existing_config.get('workspaces', {})
            has_global_oauth = 'oauth' in existing_config

            # Fields that should be preserved when masked (old format only)
            if not has_global_oauth:
                secret_fields = ['app_secret', 'user_access_token', 'refresh_token',
                               'token_expires_at', 'refresh_token_expires_at']

                for workspace_name, workspace_data in data.get('workspaces', {}).items():
                    if workspace_name in existing_workspaces:
                        existing_workspace = existing_workspaces[workspace_name]
                        for field in secret_fields:
                            incoming_value = workspace_data.get(field)
                            if (incoming_value == '***' or
                                incoming_value == '' or
                                (field in existing_workspace and incoming_value == existing_workspace[field])):
                                if field in existing_workspace:
                                    workspace_data[field] = existing_workspace[field]

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

        请求体（两种模式）：

        模式1 - 使用已保存的工作区配置：
        - workspace: 工作区名称（将从配置文件读取完整的凭据）

        模式2 - 使用提供的凭据：
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

            # Mode 1: Test using saved workspace config
            workspace_name = data.get('workspace')
            if workspace_name:
                try:
                    workspace_config = Config.get_feishu_workspace_config(workspace_name)

                    # Use the saved config for testing
                    service = get_feishu_service()
                    result = service.test_connection({
                        "app_id": workspace_config.get("app_id", ""),
                        "app_secret": workspace_config.get("app_secret", ""),
                        "user_access_token": workspace_config.get("user_access_token", ""),
                        "base_url": workspace_config.get("base_url", ""),
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
                    return jsonify({
                        "success": False,
                        "error": f"无法加载工作区配置: {str(e)}"
                    }), 400

            # Mode 2: Test using provided credentials
            app_id = data.get('app_id')
            app_secret = data.get('app_secret')
            user_access_token = data.get('user_access_token', '')
            base_url = data.get('base_url')

            if not app_id or not app_secret or not base_url:
                return jsonify({
                    "success": False,
                    "error": "参数错误：请提供 workspace 参数或完整的凭据信息（app_id、app_secret、base_url）。"
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

    # ==================== 图片代理 ====================

    @reference_bp.route('/reference/image/<file_token>', methods=['GET'])
    def get_feishu_image(file_token):
        """
        代理获取飞书图片

        此接口用于从飞书获取图片数据，自动处理 user_token 刷新。

        路径参数：
        - file_token: 飞书文件 token

        返回：
        - 成功：图片二进制数据
        - 失败：JSON 错误信息
        """
        try:
            # Get workspace configuration
            workspace_name = request.args.get('workspace')
            if not workspace_name:
                workspace_name = Config.get_active_feishu_workspace()
            workspace_config = Config.get_feishu_workspace_config(workspace_name)

            # Configure service
            service = get_feishu_service()
            service.configure(workspace_name, workspace_config)

            # Download image (returns both data and content type)
            image_data, content_type = service.download_image(file_token)

            return Response(
                image_data,
                mimetype=content_type,
                headers={
                    'Cache-Control': 'public, max-age=86400',  # Cache for 1 day
                }
            )

        except ValueError as e:
            error_msg = str(e)
            # Log the ValueError for debugging
            logger.error(f"获取飞书图片失败 (ValueError): {error_msg}")
            # Check if this is a token refresh error requiring re-auth
            if "refresh_token" in error_msg or "重新授权" in error_msg or "已过期" in error_msg:
                return jsonify({
                    "success": False,
                    "error": error_msg,
                    "requires_reauth": True
                }), 403  # Forbidden - requires re-authorization
            return jsonify({
                "success": False,
                "error": f"参数错误。\n错误详情: {error_msg}"
            }), 400
        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取飞书图片失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"获取飞书图片失败。\n错误详情: {error_msg}"
            }), 500

    @reference_bp.route('/reference/fetch-images', methods=['POST'])
    def fetch_note_images():
        """
        从现有URL下载图片

        请求体：
        - record_id: 记录ID
        - note_link: 笔记链接
        - existing_images: 已有的图片URL列表

        返回：
        - success: 是否成功
        - images: 图片路径列表
        - count: 图片数量
        """
        try:
            from backend.services.xhs_image_fetcher import XHSImageFetcher
            from backend.config import Config

            data = request.get_json()
            record_id = data.get('record_id')
            note_link = data.get('note_link')
            existing_images = data.get('existing_images', [])

            if not record_id:
                return jsonify({
                    "success": False,
                    "error": "missing_record_id"
                }), 400

            storage_path = Config.get_reference_images_path()
            fetcher = XHSImageFetcher(timeout=30)
            result = fetcher.fetch_and_save(
                record_id=record_id,
                note_link=note_link or '',
                save_dir=storage_path,
                existing_images=existing_images
            )

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"获取图片失败: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "internal_error",
                "message": f"获取图片失败: {str(e)}"
            }), 500


    @reference_bp.route('/reference-images/<record_id>/check', methods=['GET'])
    def check_reference_images(record_id: str):
        """
        检查本地是否有图片

        返回：
        - exists: 是否有本地图片
        - images: 图片路径列表
        - count: 图片数量
        - source: "local"
        """
        try:
            from backend.services.xhs_image_fetcher import XHSImageFetcher
            from backend.config import Config

            storage_path = Config.get_reference_images_path()
            record_dir = storage_path / record_id

            fetcher = XHSImageFetcher()
            result = fetcher.get_local_images(record_dir, record_id)

            if result.get("success"):
                return jsonify({
                    "exists": True,
                    "images": result["images"],
                    "count": result["count"],
                    "source": "local"
                }), 200
            else:
                return jsonify({
                    "exists": False,
                    "images": []
                }), 200

        except Exception as e:
            logger.error(f"检查图片失败: {e}")
            return jsonify({"error": str(e)}), 500


    @reference_bp.route('/reference-images/<record_id>/<filename>', methods=['GET'])
    def serve_reference_image(record_id: str, filename: str):
        """提供已下载的参考图片"""
        try:
            from backend.config import Config
            from flask import send_from_directory

            storage_path = Config.get_reference_images_path()
            record_dir = storage_path / record_id

            if not record_dir.exists():
                return jsonify({"error": "图片不存在"}), 404

            return send_from_directory(str(record_dir), filename)

        except Exception as e:
            logger.error(f"提供图片失败: {e}")
            return jsonify({"error": str(e)}), 500

    return reference_bp
