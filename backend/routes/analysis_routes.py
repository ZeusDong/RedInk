"""
对标分析 API 路由

提供待分析笔记列表的 CRUD 操作 API
"""

import json
import logging
from flask import Blueprint, request, jsonify, Response

logger = logging.getLogger(__name__)

# 模块级别的日志 - 确认模块是否被加载
logger.info("[ANALYSIS_ROUTES] Module loading...")

# 尝试导入服务
try:
    from backend.services.analysis_service import get_analysis_service
    logger.info("[ANALYSIS_ROUTES] Service import successful")
except ImportError as e:
    logger.error(f"[ANALYSIS_ROUTES] Service import failed: {e}", exc_info=True)
    raise


def create_analysis_blueprint():
    """创建对标分析 API Blueprint（工厂函数，支持多次调用）"""
    logger.info("[ANALYSIS_ROUTES] Creating analysis blueprint...")
    # 注意：不要加 /api 前缀，因为主蓝图已经有了
    analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')

    @analysis_bp.route('/pending', methods=['GET'])
    def get_pending_notes():
        """
        获取所有待分析笔记

        GET /api/analysis/pending
        Query params:
            - status: 可选的状态过滤 ('pending', 'completed', 'failed')
        """
        logger.info("[ANALYSIS_ROUTES] GET /api/analysis/pending - Fetching pending notes")
        try:
            service = get_analysis_service()
            logger.debug(f"[ANALYSIS_ROUTES] Service instance: {service}")

            # 获取状态过滤参数
            status = request.args.get('status')
            if status:
                logger.info(f"[ANALYSIS_ROUTES] Filtering by status: {status}")

            notes = service.get_pending_notes(status=status)
            logger.info(f"[ANALYSIS_ROUTES] Found {len(notes)} pending notes (status={status or 'all'})")
            return jsonify({
                'success': True,
                'data': notes,
                'count': len(notes)
            })
        except Exception as e:
            logger.error(f"[ANALYSIS_ROUTES] Error in get_pending_notes: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @analysis_bp.route('/pending', methods=['POST'])
    def add_pending_notes():
        """
        添加待分析笔记（支持批量）

        POST /api/analysis/pending
        Body: { "records": [...] }
        """
        logger.info("[ANALYSIS_ROUTES] POST /api/analysis/pending - Adding pending notes")
        try:
            data = request.get_json()
            logger.debug(f"[ANALYSIS_ROUTES] Request data: {data}")

            if not data or 'records' not in data:
                logger.warning("[ANALYSIS_ROUTES] Missing 'records' parameter in request")
                return jsonify({'success': False, 'error': '缺少 records 参数'}), 400

            service = get_analysis_service()
            logger.debug(f"[ANALYSIS_ROUTES] Service instance: {service}")

            records = data['records']
            logger.info(f"[ANALYSIS_ROUTES] Attempting to add {len(records)} records")

            count = service.add_pending_notes(records)

            logger.info(f"[ANALYSIS_ROUTES] Successfully added {count} pending notes")
            return jsonify({
                'success': True,
                'added': count,
                'message': f'成功添加 {count} 条笔记'
            })
        except Exception as e:
            logger.error(f"[ANALYSIS_ROUTES] Error in add_pending_notes: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @analysis_bp.route('/pending/<record_id>', methods=['DELETE'])
    def remove_pending_note(record_id: str):
        """
        移除待分析笔记

        DELETE /api/analysis/pending/<record_id>
        """
        service = get_analysis_service()
        success = service.remove_pending_note(record_id)

        if success:
            return jsonify({'success': True, 'message': '已移除'})
        else:
            return jsonify({'success': False, 'error': '笔记不存在'}), 404

    @analysis_bp.route('/pending', methods=['DELETE'])
    def clear_pending_notes():
        """
        清空所有待分析笔记

        DELETE /api/analysis/pending
        """
        service = get_analysis_service()
        success = service.clear_pending_notes()

        if success:
            return jsonify({'success': True, 'message': '已清空所有笔记'})
        else:
            return jsonify({'success': False, 'error': '操作失败'}), 500

    @analysis_bp.route('/pending/count', methods=['GET'])
    def get_pending_count():
        """
        获取待分析笔记数量

        GET /api/analysis/pending/count
        Query params:
            - status: 可选的状态过滤 ('pending', 'completed', 'failed')
        """
        service = get_analysis_service()
        status = request.args.get('status')

        # 获取指定状态的记录
        notes = service.get_pending_notes(status=status)

        return jsonify({
            'success': True,
            'count': len(notes)
        })

    @analysis_bp.route('/pending/check/<record_id>', methods=['GET'])
    def check_pending_note(record_id: str):
        """
        检查笔记是否在待分析列表中

        GET /api/analysis/pending/check/<record_id>
        """
        service = get_analysis_service()
        is_pending = service.is_pending(record_id)

        return jsonify({
            'success': True,
            'is_pending': is_pending
        })

    # ==================== 分析结果相关 API ====================

    @analysis_bp.route('/result/<record_id>', methods=['GET'])
    def get_analysis_result(record_id: str):
        """
        获取笔记的分析结果

        GET /api/analysis/result/<record_id>
        """
        service = get_analysis_service()
        result = service.get_analysis_result(record_id)

        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': True,
                'data': None
            })

    @analysis_bp.route('/result', methods=['POST'])
    def set_analysis_result():
        """
        设置笔记的分析结果

        POST /api/analysis/result
        Body: {
            "record_id": str,
            "analyzed": bool,
            "content": str (optional)
        }
        """
        logger.info("[ANALYSIS_ROUTES] POST /api/analysis/result - Setting analysis result")
        try:
            data = request.get_json()
            logger.debug(f"[ANALYSIS_ROUTES] Request data: {data}")

            if not data or 'record_id' not in data:
                logger.warning("[ANALYSIS_ROUTES] Missing 'record_id' parameter in request")
                return jsonify({'success': False, 'error': '缺少 record_id 参数'}), 400

            service = get_analysis_service()
            record_id = data['record_id']
            analyzed = data.get('analyzed', False)
            content = data.get('content')

            logger.info(f"[ANALYSIS_ROUTES] Setting analysis result for record_id={record_id}, analyzed={analyzed}")

            success = service.set_analysis_result(record_id, analyzed, content)

            if success:
                logger.info(f"[ANALYSIS_ROUTES] Successfully saved analysis result for record_id={record_id}")
                return jsonify({'success': True, 'message': '分析结果已保存'})
            else:
                logger.error(f"[ANALYSIS_ROUTES] Failed to save analysis result for record_id={record_id}")
                return jsonify({'success': False, 'error': '保存失败'}), 500
        except Exception as e:
            logger.error(f"[ANALYSIS_ROUTES] Error in set_analysis_result: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @analysis_bp.route('/results', methods=['GET'])
    def get_all_analysis_results():
        """
        获取所有分析结果

        GET /api/analysis/results
        """
        service = get_analysis_service()
        results = service.get_all_analysis_results()

        return jsonify({
            'success': True,
            'data': results
        })

    # ==================== Draft Management API ====================

    @analysis_bp.route('/draft', methods=['GET'])
    def get_draft():
        """
        获取指定记录的草稿数据

        GET /api/analysis/draft?record_id={id}
        """
        record_id = request.args.get('record_id')
        if not record_id:
            return jsonify({'success': False, 'error': '缺少 record_id 参数'}), 400

        service = get_analysis_service()
        draft = service.get_draft(record_id)

        if draft:
            return jsonify({
                'success': True,
                'data': draft
            })
        else:
            return jsonify({
                'success': True,
                'data': None
            })

    @analysis_bp.route('/draft', methods=['POST'])
    def save_draft():
        """
        保存草稿

        POST /api/analysis/draft
        Body: {...草稿数据...}
        """
        logger.info("[ANALYSIS_ROUTES] POST /api/analysis/draft - Saving draft")
        try:
            data = request.get_json()
            logger.debug(f"[ANALYSIS_ROUTES] Request data: {data}")

            if not data or 'record_id' not in data:
                logger.warning("[ANALYSIS_ROUTES] Missing 'record_id' parameter in request")
                return jsonify({'success': False, 'error': '缺少 record_id 参数'}), 400

            service = get_analysis_service()
            draft = service.save_draft(data)

            logger.info(f"[ANALYSIS_ROUTES] Draft saved successfully: record_id={data['record_id']}")
            return jsonify({
                'success': True,
                'data': draft,
                'message': '草稿已保存'
            })
        except Exception as e:
            logger.error(f"[ANALYSIS_ROUTES] Error in save_draft: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @analysis_bp.route('/submit', methods=['POST'])
    def submit_analysis():
        """
        提交分析

        POST /api/analysis/submit
        Body: {...分析数据...}
        """
        logger.info("[ANALYSIS_ROUTES] POST /api/analysis/submit - Submitting analysis")
        try:
            data = request.get_json()
            logger.debug(f"[ANALYSIS_ROUTES] Request data: {data}")

            if not data or 'record_id' not in data:
                logger.warning("[ANALYSIS_ROUTES] Missing 'record_id' parameter in request")
                return jsonify({'success': False, 'error': '缺少 record_id 参数'}), 400

            service = get_analysis_service()
            result = service.submit_analysis(data)

            logger.info(f"[ANALYSIS_ROUTES] Analysis submitted successfully: record_id={data['record_id']}")
            return jsonify({
                'success': True,
                'data': result,
                'message': '分析已提交'
            })
        except Exception as e:
            logger.error(f"[ANALYSIS_ROUTES] Error in submit_analysis: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==================== Visual Description Generation ====================

    @analysis_bp.route('/visual-desc', methods=['POST'])
    def generate_visual_description():
        """
        AI 生成视觉描述

        POST /api/analysis/visual-desc
        Body: {
            "record_id": str,
            "image_indices": int[]  # -1=封面图, 0,1,2...=内容图
        }
        """
        logger.info("[ANALYSIS_ROUTES] POST /api/analysis/visual-desc - Generating visual description")
        try:
            data = request.get_json()
            logger.debug(f"[ANALYSIS_ROUTES] Request data: {data}")

            if not data or 'record_id' not in data:
                logger.warning("[ANALYSIS_ROUTES] Missing 'record_id' parameter in request")
                return jsonify({'success': False, 'error': '缺少 record_id 参数'}), 400

            record_id = data['record_id']
            image_indices = data.get('image_indices', [])

            if not image_indices:
                logger.warning("[ANALYSIS_ROUTES] Missing 'image_indices' parameter in request")
                return jsonify({'success': False, 'error': '缺少 image_indices 参数'}), 400

            service = get_analysis_service()
            result = service.generate_visual_description(record_id, image_indices)

            if 'error' in result:
                logger.warning(f"[ANALYSIS_ROUTES] Visual description generation failed: {result['error']}")
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500

            logger.info(f"[ANALYSIS_ROUTES] Visual description generated successfully: record_id={record_id}")
            return jsonify({
                'success': True,
                'data': result
            })
        except ValueError as e:
            logger.error(f"[ANALYSIS_ROUTES] ValueError in generate_visual_description: {e}")
            return jsonify({'success': False, 'error': str(e)}), 404
        except Exception as e:
            logger.error(f"[ANALYSIS_ROUTES] Error in generate_visual_description: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    # ==================== AI Analysis SSE Streaming ====================

    @analysis_bp.route('/analyze-stream', methods=['POST'])
    def analyze_stream():
        """
        AI 分析（SSE 流式输出）

        POST /api/analysis/analyze-stream
        Body: {
            "record_id": str,
            "draft_data": {...}
        }
        """
        logger.info("[ANALYSIS_ROUTES] POST /api/analysis/analyze-stream - Starting AI analysis")

        # Extract request data HERE (outside generator) while request context is available
        data = request.get_json()
        record_id = data.get('record_id')
        draft_data = data.get('draft_data', {})

        def generate():
            """SSE event generator"""
            try:
                # Use data extracted from outer scope (closure)
                if not record_id:
                    yield f"event: error\ndata: {json.dumps({'error': '缺少 record_id'}, ensure_ascii=False)}\n\n"
                    return

                service = get_analysis_service()

                # Stream analysis events
                for event in service.perform_ai_analysis(record_id, draft_data):
                    event_type = event["event"]
                    event_data = event["data"]
                    yield f"event: {event_type}\ndata: {json.dumps(event_data, ensure_ascii=False)}\n\n"

            except Exception as e:
                logger.error(f"[ANALYSIS_ROUTES] Error in analyze_stream: {e}", exc_info=True)
                yield f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        return Response(generate(), mimetype='text/event-stream', headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        })

    return analysis_bp
