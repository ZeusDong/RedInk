"""
图片代理上传 API 路由

提供图片上传到图床的 REST API 接口。
"""

import logging
import os
from flask import Blueprint, jsonify, request

from backend.services.image_proxy_service import get_image_proxy_service

logger = logging.getLogger(__name__)


def create_image_proxy_blueprint() -> Blueprint:
    """
    创建图片代理上传蓝图

    Returns:
        配置好的 image_proxy_bp Blueprint
    """
    image_proxy_bp = Blueprint('image_proxy', __name__)

    @image_proxy_bp.route('/image-proxy/upload', methods=['POST'])
    def upload_image():
        """
        上传图片到图床

        请求格式：
        - multipart/form-data
          - image: 图片文件

        返回：
        - success: 是否成功
        - url: 图片URL（成功时）
        - error: 错误信息（失败时）
        """
        try:
            # 检查是否有上传的文件
            if 'image' not in request.files:
                return jsonify({'success': False, 'error': '未找到图片文件'}), 400

            file = request.files['image']

            # 检查文件名是否为空
            if file.filename == '':
                return jsonify({'success': False, 'error': '文件名为空'}), 400

            # 检查文件扩展名
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                return jsonify({'success': False, 'error': '不支持的文件类型'}), 400

            # 保存到临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
                file.save(tmp_file.name)
                tmp_path = tmp_file.name

            try:
                # 调用图片代理服务上传
                service = get_image_proxy_service()
                success, result = service.upload_image(tmp_path)

                if success:
                    return jsonify({'success': True, 'url': result})
                else:
                    return jsonify({'success': False, 'error': result}), 400

            finally:
                # 删除临时文件
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        except Exception as e:
            logger.error(f"[IMAGE_PROXY_ROUTES] 上传异常: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    return image_proxy_bp
