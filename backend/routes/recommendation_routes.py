"""
推荐API路由 V2.0

提供基于AI分析的智能推荐功能，包含缓存管理
"""

import logging
from flask import Blueprint, request, jsonify
from backend.services.recommendation_service import get_recommendation_service_v2

logger = logging.getLogger(__name__)


def create_recommendation_blueprint():
    """创建推荐API蓝图 V2.0"""
    bp = Blueprint('recommendation', __name__, url_prefix='/recommendations')

    # ==================== 推荐搜索 ====================

    @bp.route('', methods=['POST'])
    def recommend():
        """
        获取推荐列表 V2.0

        请求体:
        {
            "topic": "春季护肤",
            "industry": "美妆护肤",     // 可选
            "scenario": "beginner",       // 可选：beginner|trending|quality
            "limit": 20                  // 可选，默认20
        }

        返回:
        {
            "success": true,
            "data": {
                "topic": "春季护肤",
                "scenario": "beginner",
                "total": 15,
                "results": [...]
            }
        }
        """
        try:
            data = request.get_json()
            topic = data.get('topic', '').strip()

            if not topic:
                return jsonify({
                    'success': False,
                    'error': '请输入搜索主题'
                }), 400

            industry = data.get('industry')
            scenario = data.get('scenario')
            limit = min(data.get('limit', 20), 50)  # 最大50条

            service = get_recommendation_service_v2()
            results = service.get_recommendations(
                topic=topic,
                industry=industry,
                scenario=scenario,
                limit=limit
            )

            logger.info(f"[RECOMMEND_V2] Query: topic={topic}, results={len(results)}")

            return jsonify({
                'success': True,
                'data': {
                    'topic': topic,
                    'scenario': scenario,
                    'total': len(results),
                    'results': results
                }
            })

        except Exception as e:
            logger.error(f"[RECOMMEND_V2] Query failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # ==================== 相似推荐 ====================

    @bp.route('/similar/<record_id>', methods=['GET'])
    def recommend_similar(record_id: str):
        """
        获取相似推荐

        Args:
            record_id: 记录ID

        Query Params:
            limit: 返回数量限制，默认10

        返回:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            limit = min(request.args.get('limit', 10, type=int), 50)

            service = get_recommendation_service_v2()
            results = service.recommend_similar(
                record_id=record_id,
                limit=limit
            )

            logger.info(f"[RECOMMEND_V2] Similar: record_id={record_id}, results={len(results)}")

            return jsonify({
                'success': True,
                'data': results
            })

        except Exception as e:
            logger.error(f"[RECOMMEND_V2] Similar failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # ==================== 行业列表 ====================

    @bp.route('/industries', methods=['GET'])
    def get_industries():
        """
        获取可用的行业列表

        返回:
        {
            "success": true,
            "data": ["美妆护肤", "美食", "旅行", ...]
        }
        """
        try:
            service = get_recommendation_service_v2()

            # 从已分析的笔记中提取行业
            analyzed = service._get_analyzed_records()
            industries = set()
            for record in analyzed.values():
                industry = record.get('industry')
                if industry:
                    industries.add(industry)

            result = sorted(list(industries))

            logger.info(f"[RECOMMEND_V2] Industries: count={len(result)}")

            return jsonify({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f"[RECOMMEND_V2] Industries failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # ==================== 缓存管理 ====================

    @bp.route('/cache', methods=['DELETE'])
    def clear_cache():
        """
        清除推荐缓存

        请求体:
        {
            "target": "all",              // all|expired|record
            "record_id": "xxx",           // target='record' 时必需
            "older_than_days": 7           // target='expired' 时，默认7天
        }

        返回:
        {
            "success": true,
            "data": {
                "cleared_count": 15
            }
        }
        """
        try:
            data = request.get_json() or {}
            target = data.get('target', 'all')
            record_id = data.get('record_id')
            older_than_days = data.get('older_than_days', 7)

            service = get_recommendation_service_v2()
            cleared = service.clear_cache(
                target=target,
                record_id=record_id,
                older_than_days=older_than_days
            )

            logger.info(f"[RECOMMEND_V2] Cache cleared: target={target}, count={cleared}")

            return jsonify({
                'success': True,
                'data': {
                    'cleared_count': cleared
                }
            })

        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        except Exception as e:
            logger.error(f"[RECOMMEND_V2] Cache clear failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/cache/stats', methods=['GET'])
    def get_cache_stats():
        """
        获取缓存统计

        返回:
        {
            "success": true,
            "data": {
                "total_entries": 100,
                "expired_entries": 15
            }
        }
        """
        try:
            service = get_recommendation_service_v2()
            stats = service.get_cache_stats()

            logger.info(f"[RECOMMEND_V2] Cache stats: total={stats['total_entries']}, expired={stats['expired_entries']}")

            return jsonify({
                'success': True,
                'data': stats
            })

        except Exception as e:
            logger.error(f"[RECOMMEND_V2] Cache stats failed: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    logger.info("✅ Recommendation V2.0 routes registered")
    return bp
