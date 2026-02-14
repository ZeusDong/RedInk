"""
推荐API路由

提供基于主题的智能推荐功能
"""

import logging
from flask import Blueprint, request, jsonify
from backend.services.recommendation_service import get_recommendation_service

logger = logging.getLogger(__name__)


def create_recommendation_blueprint():
    """创建推荐API蓝图"""
    bp = Blueprint('recommendation', __name__)

    @bp.route('/recommend', methods=['POST'])
    def recommend():
        """
        获取推荐列表

        请求体:
        {
            "topic": "春季护肤",
            "industry": "美妆护肤",  // 可选
            "scenario": "beginner",    // 可选：beginner/trending/quality
            "limit": 20                // 可选，默认20
        }

        Returns:
        {
            "success": true,
            "data": [
                {
                    "record_id": "xxx",
                    "record": {...},
                    "match_score": 0.85,
                    "reasons": ["industry", "keyword"],
                    "scores": {...}
                },
                ...
            ]
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
            limit = data.get('limit', 20)

            service = get_recommendation_service()
            recommendations = service.get_recommendations(
                topic=topic,
                industry=industry,
                scenario=scenario,
                limit=limit
            )

            logger.info(f"📊 推荐查询: topic={topic}, results={len(recommendations)}")

            return jsonify({
                'success': True,
                'data': recommendations
            })

        except Exception as e:
            logger.error(f"❌ 推荐查询失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/recommend/similar/<record_id>', methods=['GET'])
    def recommend_similar(record_id: str):
        """
        获取相似推荐

        Args:
            record_id: 记录ID

        Query Params:
            limit: 返回数量限制，默认10

        Returns:
        {
            "success": true,
            "data": [...]
        }
        """
        try:
            limit = request.args.get('limit', 10, type=int)

            service = get_recommendation_service()
            recommendations = service.recommend_similar(
                record_id=record_id,
                limit=limit
            )

            logger.info(f"📊 相似推荐: record_id={record_id}, results={len(recommendations)}")

            return jsonify({
                'success': True,
                'data': recommendations
            })

        except Exception as e:
            logger.error(f"❌ 相似推荐失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @bp.route('/recommend/industries', methods=['GET'])
    def get_industries():
        """
        获取可用的行业列表

        Returns:
        {
            "success": true,
            "data": ["美妆护肤", "美食", "旅行", ...]
        }
        """
        try:
            service = get_recommendation_service()

            # 从对标数据中提取所有行业
            industries = set()
            for record in service.reference_db.values():
                industry = record.get('industry')
                if industry:
                    industries.add(industry)

            result = sorted(list(industries))

            logger.info(f"📊 行业列表: count={len(result)}")

            return jsonify({
                'success': True,
                'data': result
            })

        except Exception as e:
            logger.error(f"❌ 获取行业列表失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    logger.debug("✅ Recommendation routes registered")
    return bp
