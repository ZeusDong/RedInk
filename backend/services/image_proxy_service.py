"""
图片代理上传服务

将图片上传到图床服务，获取稳定的图片URL。
API 文档: https://imageproxy.zhongzhuan.chat

用于解决小红书外部链接403反盗链问题。
"""

import logging
import requests
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class ImageProxyService:
    """图片代理上传服务

    API 文档: https://imageproxy.zhongzhuan.chat
    """

    def __init__(self):
        """初始化图片代理服务"""
        self.api_url = "https://imageproxy.zhongzhuan.chat/api/upload"

    def upload_image(self, image_path: str) -> Tuple[bool, str]:
        """
        上传图片到图床

        Args:
            image_path: 图片本地路径

        Returns:
            Tuple[success, url_or_error]: (成功, 图片URL) 或 (失败, 错误信息)
        """
        try:
            # 读取图片数据 - 文件必须在请求期间保持打开
            with open(image_path, 'rb') as f:
                files = {'file': f}
                # 发送请求（requests 自动处理 multipart/form-data）
                response = requests.post(
                    self.api_url,
                    files=files,
                    timeout=60
                )

            if response.status_code == 200:
                result = response.json()
                if result.get('url'):
                    url = result['url']
                    logger.info(f"[IMAGE_PROXY] 上传成功: {image_path} -> {url}")
                    return True, url
                else:
                    error_msg = result.get('error') or result.get('message') or '未知错误'
                    logger.warning(f"[IMAGE_PROXY] 上传失败: {error_msg}")
                    return False, f"上传失败: {error_msg}"
            else:
                error_msg = response.text[:200] if response.text else f'HTTP {response.status_code}'
                logger.error(f"[IMAGE_PROXY] 请求失败: {response.status_code} - {error_msg}")
                return False, f"请求失败 ({response.status_code})"

        except FileNotFoundError:
            logger.error(f"[IMAGE_PROXY] 文件不存在: {image_path}")
            return False, f"文件不存在: {image_path}"
        except Exception as e:
            logger.error(f"[IMAGE_PROXY] 上传异常: {e}")
            return False, f"上传异常: {str(e)}"


# 全局服务实例
_image_proxy_service: Optional[ImageProxyService] = None


def get_image_proxy_service() -> ImageProxyService:
    """
    获取图片代理服务单例

    Returns:
        ImageProxyService实例
    """
    global _image_proxy_service
    if _image_proxy_service is None:
        _image_proxy_service = ImageProxyService()
    return _image_proxy_service
