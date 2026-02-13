"""
AI总结 API 路由

提供 AI 总结的 CRUD 操作 API，以及流式生成接口
"""

import json
import logging
from flask import Blueprint, request, jsonify, Response

logger = logging.getLogger(__name__)

# 模块级别的日志 - 确认模块是否被加载
logger.info("[SUMMARY_ROUTES] Module loading...")

# 尝试导入服务
try:
    from backend.services.summary_service import get_summary_service
    from backend.services.analysis_service import get_analysis_service
    logger.info("[SUMMARY_ROUTES] Service import successful")
except ImportError as e:
    logger.error(f"[SUMMARY_ROUTES] Service import failed: {e}", exc_info=True)
    raise


def create_summary_blueprint():
    """创建 AI 总结 API Blueprint（工厂函数，支持多次调用）"""
    logger.info("[SUMMARY_ROUTES] Creating summary blueprint...")
    summary_bp = Blueprint('summary', __name__, url_prefix='/summary')

    @summary_bp.route('', methods=['GET'])
    def get_all_summaries():
        """
        获取所有总结（按行业分组）

        GET /api/summary
        Query params:
            - industry: 可选的行业过滤
        """
        logger.info("[SUMMARY_ROUTES] GET /api/summary - Fetching all summaries")
        try:
            service = get_summary_service()

            # 获取行业过滤参数
            industry = request.args.get('industry')

            if industry:
                summaries = service.get_summaries_by_industry(industry)
                logger.info(f"[SUMMARY_ROUTES] Found {len(summaries)} summaries for industry={industry}")
            else:
                summaries = service.get_all_summaries()
                logger.info(f"[SUMMARY_ROUTES] Found {len(summaries)} total summaries")

            return jsonify({
                'success': True,
                'data': summaries,
                'count': len(summaries)
            })
        except Exception as e:
            logger.error(f"[SUMMARY_ROUTES] Error in get_all_summaries: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @summary_bp.route('/industries', methods=['GET'])
    def get_industries():
        """
        获取所有有总结的行业列表

        GET /api/summary/industries
        """
        logger.info("[SUMMARY_ROUTES] GET /api/summary/industries - Fetching industries")
        try:
            service = get_summary_service()
            industries = service.get_industries()

            logger.info(f"[SUMMARY_ROUTES] Found {len(industries)} industries")
            return jsonify({
                'success': True,
                'data': industries,
                'count': len(industries)
            })
        except Exception as e:
            logger.error(f"[SUMMARY_ROUTES] Error in get_industries: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @summary_bp.route('/<int:summary_id>', methods=['GET'])
    def get_summary(summary_id: int):
        """
        获取单个总结详情

        GET /api/summary/<id>
        """
        logger.info(f"[SUMMARY_ROUTES] GET /api/summary/{summary_id} - Fetching summary")
        try:
            service = get_summary_service()
            summary = service.get_summary(summary_id)

            if summary:
                return jsonify({
                    'success': True,
                    'data': summary
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '总结不存在'
                }), 404
        except Exception as e:
            logger.error(f"[SUMMARY_ROUTES] Error in get_summary: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @summary_bp.route('/<int:summary_id>', methods=['DELETE'])
    def delete_summary(summary_id: int):
        """
        删除总结

        DELETE /api/summary/<id>
        """
        logger.info(f"[SUMMARY_ROUTES] DELETE /api/summary/{summary_id} - Deleting summary")
        try:
            service = get_summary_service()
            success = service.delete_summary(summary_id)

            if success:
                return jsonify({
                    'success': True,
                    'message': '总结已删除'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '总结不存在'
                }), 404
        except Exception as e:
            logger.error(f"[SUMMARY_ROUTES] Error in delete_summary: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @summary_bp.route('/generate', methods=['POST'])
    def generate_summary():
        """
        生成 AI 总结（SSE 流式输出）

        POST /api/summary/generate
        Body: {
            "record_ids": ["record_id_1", "record_id_2", ...],
            "industry": "美妆护肤"
        }
        """
        logger.info("[SUMMARY_ROUTES] POST /api/summary/generate - Starting summary generation")

        # Extract request data HERE (outside generator) while request context is available
        data = request.get_json()
        if not data:
            yield f"event: error\ndata: {json.dumps({'error': '缺少请求体'}, ensure_ascii=False)}\n\n"
            return

        record_ids = data.get('record_ids', [])
        industry = data.get('industry', '')

        def generate():
            """SSE event generator"""
            try:
                # 验证参数
                if not record_ids:
                    yield f"event: error\ndata: {json.dumps({'error': '缺少 record_ids 参数'}, ensure_ascii=False)}\n\n"
                    return

                if not industry:
                    yield f"event: error\ndata: {json.dumps({'error': '缺少 industry 参数'}, ensure_ascii=False)}\n\n"
                    return

                service = get_summary_service()

                # Stream summary generation events
                for event in service.generate_summary(industry, record_ids):
                    event_type = event["event"]
                    event_data = event["data"]
                    yield f"event: {event_type}\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"

            except Exception as e:
                logger.error(f"[SUMMARY_ROUTES] Error in generate_summary: {e}", exc_info=True)
                yield f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        return Response(generate(), mimetype='text/event-stream', headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        })

    return summary_bp
