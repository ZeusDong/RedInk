"""
测试接口相关路由

包含功能：
- 测试采集：采集指定多维表格的数据并保存到独立缓存文件
"""

import logging
from flask import Blueprint, request, jsonify
from backend.config import Config
from backend.services.feishu_service import get_feishu_service

logger = logging.getLogger(__name__)


def create_reference_test_blueprint():
    """创建测试接口路由蓝图（工厂函数，支持多次调用）"""
    reference_test_bp = Blueprint('reference_test', __name__)

    @reference_test_bp.route('/reference/test-fetch', methods=['POST'])
    def test_fetch():
        """
        测试采集多维表格数据

        从指定的多维表格采集数据并保存到独立的缓存文件，用于快速测试新的表格配置。

        请求体：
        - workspace: 工作区/测试表格配置名称（必填）
        - sample_count: 返回的示例数据数量（可选，默认 5）

        返回：
        - success: 是否成功
        - message: 结果消息
        - data: 采集结果数据
          - workspace: 工作区名称
          - app_token: 多维表格应用令牌
          - table_name: 表格名称
          - table_id: 表格 ID
          - total_records: 采集的总记录数
          - fetch_time_ms: 采集耗时（毫秒）
          - cached_at: 缓存时间
          - cache_file: 缓存文件路径
          - sample_records: 示例记录列表（已转换为 ReferenceRecord 格式）

        示例请求：
        POST /api/reference/test-fetch
        {
          "workspace": "test_table_1",
          "sample_count": 5
        }
        """
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    "success": False,
                    "error": "参数错误：请求体不能为空。"
                }), 400

            workspace_name = data.get('workspace')
            if not workspace_name:
                return jsonify({
                    "success": False,
                    "error": "参数错误：workspace 字段不能为空。"
                }), 400

            sample_count = int(data.get('sample_count', 5))

            # Get workspace configuration
            try:
                workspace_config = Config.get_feishu_workspace_config(workspace_name)
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"配置 '{workspace_name}' 不存在或加载失败。\n"
                            f"请先在 feishu_providers.yaml 中添加该配置。\n"
                            f"错误详情: {str(e)}"
                }), 404

            # Use FeishuService to test fetch records
            service = get_feishu_service()
            result = service.test_fetch_records(
                workspace_name=workspace_name,
                config=workspace_config,
                sample_count=sample_count
            )

            if result.get("success"):
                return jsonify({
                    "success": True,
                    "message": result.get("message"),
                    "data": result.get("data", {})
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": result.get("error", "采集失败")
                }), 400

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
            logger.error(f"测试采集失败: {error_msg}")
            return jsonify({
                "success": False,
                "error": f"测试采集失败。\n错误详情: {error_msg}"
            }), 500

    return reference_test_bp
