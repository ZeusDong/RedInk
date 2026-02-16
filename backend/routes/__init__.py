"""
API 路由模块

本模块将 API 路由按功能拆分为多个子模块：
- outline_routes: 大纲生成相关 API
- image_routes: 图片生成/获取相关 API
- history_routes: 历史记录 CRUD API
- config_routes: 配置管理 API
- content_routes: 内容生成相关 API（标题、文案、标签）
- reference_routes: 对标文案查询相关 API
- reference_test_routes: 测试接口相关 API
- oauth_routes: OAuth 授权相关 API
- analysis_routes: 对标分析相关 API
- summary_routes: AI 总结相关 API

所有路由都注册到统一的 /api 前缀下
"""

import logging
from flask import Blueprint

logger = logging.getLogger(__name__)


def create_api_blueprint():
    """
    创建并配置主 API 蓝图

    每次调用都会创建新的蓝图实例，支持多次 create_app() 调用（如测试环境）

    Returns:
        配置好的 api Blueprint
    """
    logger.debug("[ROUTES] Creating API blueprint...")

    from .outline_routes import create_outline_blueprint
    from .image_routes import create_image_blueprint
    from .history_routes import create_history_blueprint
    from .config_routes import create_config_blueprint
    from .content_routes import create_content_blueprint
    from .reference_routes import create_reference_blueprint
    from .reference_test_routes import create_reference_test_blueprint
    from .oauth_routes import create_oauth_blueprint
    from .image_proxy_routes import create_image_proxy_blueprint
    from .summary_routes import create_summary_blueprint
    from .recommendation_routes import create_recommendation_blueprint
    from .template_routes import create_template_blueprint
    from .template_group_routes import create_template_group_blueprint
    from .optimizer_routes import create_optimizer_blueprint

    # 显式捕获 analysis_routes 导入错误
    try:
        from .analysis_routes import create_analysis_blueprint
        logger.info("[ROUTES] analysis_routes module imported successfully")
    except ImportError as e:
        logger.error(f"[ROUTES] Failed to import analysis_routes: {e}", exc_info=True)
        raise

    # 创建主 API 蓝图
    api_bp = Blueprint('api', __name__, url_prefix='/api')

    # 将子蓝图注册到主蓝图（不带额外前缀）
    api_bp.register_blueprint(create_outline_blueprint())
    logger.debug("   ✅ outline_routes registered")
    api_bp.register_blueprint(create_image_blueprint())
    logger.debug("   ✅ image_routes registered")
    api_bp.register_blueprint(create_history_blueprint())
    logger.debug("   ✅ history_routes registered")
    api_bp.register_blueprint(create_config_blueprint())
    logger.debug("   ✅ config_routes registered")
    api_bp.register_blueprint(create_content_blueprint())
    logger.debug("   ✅ content_routes registered")
    api_bp.register_blueprint(create_reference_blueprint())
    logger.debug("   ✅ reference_routes registered")
    api_bp.register_blueprint(create_reference_test_blueprint())
    logger.debug("   ✅ reference_test_routes registered")
    api_bp.register_blueprint(create_oauth_blueprint())
    logger.debug("   ✅ oauth_routes registered")
    api_bp.register_blueprint(create_image_proxy_blueprint())
    logger.debug("   ✅ image_proxy_routes registered")
    api_bp.register_blueprint(create_summary_blueprint())
    logger.debug("   ✅ summary_routes registered")
    api_bp.register_blueprint(create_recommendation_blueprint())
    logger.debug("   ✅ recommendation_routes registered")
    api_bp.register_blueprint(create_template_blueprint())
    logger.debug("   ✅ template_routes registered")
    api_bp.register_blueprint(create_template_group_blueprint())
    logger.debug("   ✅ template_group_routes registered")
    api_bp.register_blueprint(create_optimizer_blueprint())
    logger.debug("   ✅ optimizer_routes registered")

    # 显式捕获 analysis_routes 蓝图创建错误
    try:
        analysis_bp = create_analysis_blueprint()
        api_bp.register_blueprint(analysis_bp)
        logger.debug("   ✅ analysis_routes registered")
    except Exception as e:
        logger.error(f"[ROUTES] Failed to create/register analysis_blueprint: {e}", exc_info=True)
        raise

    logger.info("[ROUTES] All route blueprints registered successfully")
    return api_bp


def register_routes(app):
    """
    注册所有 API 路由到 Flask 应用

    Args:
        app: Flask 应用实例
    """
    api_bp = create_api_blueprint()
    app.register_blueprint(api_bp)


__all__ = ['register_routes', 'create_api_blueprint']
