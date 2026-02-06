"""
小红书图片下载服务（简化版）
- 支持从现有URL下载图片
- 支持读取本地已放置的图片
"""
import logging
import json
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class XHSImageFetcher:
    """小红书图片下载器"""

    XHS_IMAGE_DOMAINS = [
        'sns-img-bd.xhscdn.com',
        'sns-img-qc.xhscdn.com',
        'sns-img-hk.xhscdn.com',
        'xhscdn.com'
    ]

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def get_local_images(self, record_dir: Path, record_id: str) -> Dict:
        """
        读取本地已放置的图片

        Args:
            record_dir: 记录图片目录
            record_id: 记录ID

        Returns:
            {
                "success": True,
                "images": ["/api/reference-images/xxx/0.jpg", ...],
                "count": 2,
                "source": "local"
            }
        """
        if not record_dir.exists():
            return {"success": False, "error": "directory_not_exists"}

        # 查找所有图片文件（按数字命名）
        image_files = []
        for i in range(100):  # 最多支持100张图片
            for ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                filepath = record_dir / f"{i}.{ext}"
                if filepath.exists():
                    image_files.append(f"{i}.{ext}")
                    break

        if not image_files:
            return {"success": False, "error": "no_images_found"}

        # 构建API路径
        api_paths = [
            f"/api/reference-images/{record_id}/{f}"
            for f in image_files
        ]

        return {
            "success": True,
            "images": api_paths,
            "count": len(image_files),
            "source": "local"
        }

    def fetch_and_save(
        self,
        record_id: str,
        note_link: str,
        save_dir: Path,
        existing_images: Optional[List[str]] = None
    ) -> Dict:
        """
        从现有URL下载并保存图片

        Args:
            record_id: 记录ID
            note_link: 笔记链接
            save_dir: 保存目录
            existing_images: 已有的图片URL列表

        Returns:
            {
                "success": True/False,
                "images": ["/api/reference-images/recxxx/0.jpg", ...],
                "count": 3,
                "message": "成功",
                "source": "url_download"
            }
        """
        if not existing_images:
            return {
                "success": False,
                "error": "no_urls",
                "message": "数据中没有图片链接，请手动放置图片到指定目录"
            }

        try:
            # 创建记录目录
            record_dir = save_dir / record_id
            record_dir.mkdir(parents=True, exist_ok=True)

            # 过滤出有效的图片URL
            valid_urls = [url for url in existing_images if self._is_xhs_image(url)]

            if not valid_urls:
                return {
                    "success": False,
                    "error": "no_valid_urls",
                    "message": "没有有效的小红书图片链接"
                }

            # 下载图片
            downloaded = self._download_from_urls(valid_urls, record_dir, note_link)

            if downloaded:
                # 保存元数据
                self._save_metadata(record_dir, downloaded, "url_download")
                return self._success_result(record_id, downloaded, record_dir)
            else:
                return {
                    "success": False,
                    "error": "download_failed",
                    "message": "图片下载失败，请手动放置图片"
                }

        except Exception as e:
            logger.error(f"下载图片失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": "internal_error",
                "message": f"下载失败: {str(e)}"
            }

    def _download_from_urls(
        self,
        urls: List[str],
        save_dir: Path,
        note_link: str
    ) -> List[str]:
        """从URL列表下载图片"""
        downloaded = []

        for i, url in enumerate(urls):
            try:
                if not url or not url.startswith('http'):
                    continue

                ext = self._get_image_extension(url)
                filename = f"{i}.{ext}"
                filepath = save_dir / filename

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': note_link or 'https://www.xiaohongshu.com/',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                }

                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    stream=True
                )
                response.raise_for_status()

                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                downloaded.append(filename)
                logger.info(f"下载成功: {filename}")

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    logger.warning(f"下载图片 {i} 失败: 403 Forbidden (防盗链)")
                else:
                    logger.warning(f"下载图片 {i} 失败: {e}")
            except Exception as e:
                logger.warning(f"下载图片 {i} 失败: {e}")

        return downloaded

    def _get_image_extension(self, url: str) -> str:
        """从URL获取图片扩展名"""
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            if '.jpg' in path or '.jpeg' in path:
                return 'jpg'
            elif '.png' in path:
                return 'png'
            elif '.webp' in path:
                return 'webp'
            elif '.gif' in path:
                return 'gif'
        except Exception:
            pass
        return 'jpg'

    def _is_xhs_image(self, url: str) -> bool:
        """判断是否是小红书图片URL"""
        try:
            parsed = urlparse(url)
            return any(domain in parsed.netloc for domain in self.XHS_IMAGE_DOMAINS)
        except Exception:
            return False

    def _save_metadata(self, record_dir: Path, filenames: List[str], source: str):
        """保存元数据"""
        metadata = {
            "images": [{"filename": f} for f in filenames],
            "fetched_at": datetime.now().isoformat(),
            "source": source
        }

        metadata_file = record_dir / '.metadata.json'
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _success_result(self, record_id: str, filenames: List[str], save_dir: Path) -> Dict:
        """构建成功响应"""
        api_paths = [
            f"/api/reference-images/{record_id}/{f}"
            for f in filenames
        ]

        return {
            "success": True,
            "images": api_paths,
            "count": len(filenames),
            "message": f"成功下载 {len(filenames)} 张图片",
            "source": "url_download"
        }
