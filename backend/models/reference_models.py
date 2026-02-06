"""
Data models for reference record feature.

This module defines the data structures for storing and manipulating
Xiaohongshu reference content data from Feishu Bitable.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Any, Dict


@dataclass
class BloggerInfo:
    """博主信息 - Blogger information"""
    nickname: str = ""
    blogger_id: str = ""
    homepage: str = ""
    avatar: str = ""
    bio: str = ""
    follower_count: int = 0
    following_count: int = 0
    liked_collected_count: int = 0


@dataclass
class NoteMetrics:
    """笔记指标 - Note metrics"""
    likes: int = 0
    saves: int = 0
    comments: int = 0
    total_engagement: int = 0
    save_ratio: float = 0.0
    comment_ratio: float = 0.0


@dataclass
class ReferenceRecord:
    """对标文案记录 - Reference record"""
    record_id: str = ""
    keyword: str = ""
    blogger: BloggerInfo = field(default_factory=BloggerInfo)
    title: str = ""
    body: str = ""
    cover_image: str = ""
    images: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    note_link: str = ""
    metrics: NoteMetrics = field(default_factory=NoteMetrics)
    category: str = ""
    industry: str = ""
    note_type: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "record_id": self.record_id,
            "keyword": self.keyword,
            "blogger": {
                "nickname": self.blogger.nickname,
                "blogger_id": self.blogger.blogger_id,
                "homepage": self.blogger.homepage,
                "avatar": self.blogger.avatar,
                "bio": self.blogger.bio,
                "follower_count": self.blogger.follower_count,
                "following_count": self.blogger.following_count,
                "liked_collected_count": self.blogger.liked_collected_count,
            },
            "title": self.title,
            "body": self.body,
            "cover_image": self.cover_image,
            "images": self.images,
            "tags": self.tags,
            "note_link": self.note_link,
            "metrics": {
                "likes": self.metrics.likes,
                "saves": self.metrics.saves,
                "comments": self.metrics.comments,
                "total_engagement": self.metrics.total_engagement,
                "save_ratio": self.metrics.save_ratio,
                "comment_ratio": self.metrics.comment_ratio,
            },
            "category": self.category,
            "industry": self.industry,
            "note_type": self.note_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReferenceRecord":
        """Create from dictionary."""
        blogger_data = data.get("blogger", {})
        metrics_data = data.get("metrics", {})

        return cls(
            record_id=data.get("record_id", ""),
            keyword=data.get("keyword", ""),
            blogger=BloggerInfo(
                nickname=blogger_data.get("nickname", ""),
                blogger_id=blogger_data.get("blogger_id", ""),
                homepage=blogger_data.get("homepage", ""),
                avatar=blogger_data.get("avatar", ""),
                bio=blogger_data.get("bio", ""),
                follower_count=blogger_data.get("follower_count", 0),
                following_count=blogger_data.get("following_count", 0),
                liked_collected_count=blogger_data.get("liked_collected_count", 0),
            ),
            title=data.get("title", ""),
            body=data.get("body", ""),
            cover_image=data.get("cover_image", ""),
            images=data.get("images", []),
            tags=data.get("tags", []),
            note_link=data.get("note_link", ""),
            metrics=NoteMetrics(
                likes=metrics_data.get("likes", 0),
                saves=metrics_data.get("saves", 0),
                comments=metrics_data.get("comments", 0),
                total_engagement=metrics_data.get("total_engagement", 0),
                save_ratio=metrics_data.get("save_ratio", 0.0),
                comment_ratio=metrics_data.get("comment_ratio", 0.0),
            ),
            category=data.get("category", ""),
            industry=data.get("industry", ""),
            note_type=data.get("note_type", ""),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
        )


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse datetime from string."""
    if not value:
        return None
    try:
        # Try ISO format first
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def transform_feishu_record(feishu_record: Dict[str, Any]) -> ReferenceRecord:
    """
    Transform Feishu Bitable record to ReferenceRecord.

    Args:
        feishu_record: Raw record from Feishu API

    Returns:
        ReferenceRecord: Transformed record
    """
    fields = feishu_record.get("fields", {})
    record_id = feishu_record.get("record_id", "")

    # Extract blogger info
    # Try "博主头像-text" first (Xiaohongshu CDN URL), then use proxy URL
    # Note: Feishu tmp_url requires authentication, so we always use proxy for Feishu images
    avatar_text = _get_field_value(fields, "博主头像-text", "")
    if not avatar_text:
        # Use proxy URL for Feishu images (handles authentication)
        avatar_file = fields.get("博主头像")
        file_token = _extract_file_token(avatar_file)
        if file_token:
            avatar_text = _generate_image_proxy_url(file_token)

    blogger = BloggerInfo(
        nickname=_get_field_value(fields, "博主", ""),
        blogger_id=_get_field_value(fields, "博主ID", ""),
        homepage=_get_field_value(fields, "博主主页", ""),
        avatar=avatar_text,
        bio=_get_field_value(fields, "博主简介", ""),
        follower_count=_get_field_int(fields, "博主粉丝数", 0),
        following_count=_get_field_int(fields, "博主关注数", 0),
        liked_collected_count=_get_field_int(fields, "博主获赞与收藏数", 0),
    )

    # Extract metrics
    likes = _get_field_int(fields, "点赞数", 0)
    saves = _get_field_int(fields, "收藏数", 0)
    comments = _get_field_int(fields, "评论数", 0)
    total = _get_field_int(fields, "总互动量", likes + saves + comments)

    metrics = NoteMetrics(
        likes=likes,
        saves=saves,
        comments=comments,
        total_engagement=total,
        save_ratio=_get_field_float(fields, "收藏互动比", 0.0),
        comment_ratio=_get_field_float(fields, "评论互动比", 0.0),
    )

    # Extract images
    # Priority: 1) file_token with proxy URL (handles Feishu auth), 2) 笔记封面-text (external URL)
    # Note: Feishu tmp_url requires authentication, so we use proxy URL instead
    cover_file = fields.get("笔记封面")
    file_token = _extract_file_token(cover_file)
    if file_token:
        # Use proxy URL for Feishu images (handles authentication)
        cover_image = _generate_image_proxy_url(file_token)
    else:
        # Fallback to 笔记封面-text if no file_token available
        cover_image = _get_field_value(fields, "笔记封面-text", "")
        # Convert http to https for better browser compatibility
        if cover_image and cover_image.startswith("http://"):
            cover_image = cover_image.replace("http://", "https://", 1)
    images_links = _get_field_value(fields, "笔记图片链接", "")
    images = []
    if images_links:
        if isinstance(images_links, str):
            images = [img.strip() for img in images_links.split(",") if img.strip()]
        elif isinstance(images_links, list):
            images = images_links
        # Convert http to https for better browser compatibility (fixes mixed content issues)
        images = [_convert_http_to_https(img) if isinstance(img, str) else img for img in images]

    # Extract tags
    tags_value = _get_field_value(fields, "笔记标签", "")
    tags = []
    if tags_value:
        if isinstance(tags_value, str):
            tags = [tag.strip() for tag in tags_value.split(",") if tag.strip()]
        elif isinstance(tags_value, list):
            tags = tags_value

    # Parse created_at time (Feishu uses timestamp in milliseconds)
    created_at = None
    created_time = feishu_record.get("created_time")
    if created_time:
        try:
            created_at = datetime.fromtimestamp(created_time / 1000)
        except (ValueError, TypeError):
            pass
    else:
        # Feishu records don't have created_time at record level
        # Check for alternative timestamp fields in fields object
        # Common alternatives: '创建时间', '发布时间', '记录创建时间'
        alt_time = None
        for time_key in ['创建时间', '发布时间', '记录创建时间', '创建日期', '发布日期', 'publish_time', 'create_time', 'modified_time', '更新时间']:
            field_value = _get_field_value(fields, time_key, None)
            if field_value:
                try:
                    # Try parsing as timestamp (seconds or milliseconds)
                    if isinstance(field_value, (int, float)):
                        # Check if it's in milliseconds (Feishu timestamps) or seconds
                        if field_value > 1000000000000:  # Milliseconds (year 2001+)
                            alt_time = datetime.fromtimestamp(field_value / 1000)
                        else:  # Seconds
                            alt_time = datetime.fromtimestamp(field_value)
                        break
                    elif isinstance(field_value, str):
                        # Try parsing as ISO format string
                        try:
                            alt_time = datetime.fromisoformat(field_value.replace('Z', '+00:00'))
                            break
                        except (ValueError, AttributeError):
                            continue
                except (ValueError, TypeError):
                    continue

        if alt_time:
            created_at = alt_time
        else:
            # Fallback: Use current time (when record was synced)
            created_at = datetime.now()

    # Extract industry
    industry_value = _get_field_value(fields, "笔记所属行业领域", "")

    return ReferenceRecord(
        record_id=record_id,
        keyword=_get_field_value(fields, "关键词", ""),
        blogger=blogger,
        title=_get_field_value(fields, "标题", ""),
        body=_get_field_value(fields, "正文", ""),
        cover_image=cover_image,
        images=images,
        tags=tags,
        note_link=_get_field_value(fields, "笔记链接", ""),
        metrics=metrics,
        category=_get_field_value(fields, "笔记分类", ""),
        industry=industry_value,
        note_type=_get_field_value(fields, "笔记类型", ""),
        created_at=created_at,
        updated_at=None,
    )


def _get_field_value(fields: Dict[str, Any], key: str, default: Any = "") -> Any:
    """Get field value from Feishu fields dict.

    Feishu returns fields in different formats:
    1. Plain string: "value" (e.g., "笔记所属行业领域": "服饰穿搭")
    2. Plain number: 1234 (e.g., "点赞数": 3648, "收藏数": 3526)
    3. Simple text: [{"text": "value", "type": "text"}]
    4. Rich text: {"type": 1, "value": [{"text": "value", "type": "text"}]}
    This function extracts the actual value from those structures.
    """
    if key not in fields:
        return default

    value = fields[key]
    if value is None:
        return default

    # Handle plain string values (e.g., "笔记所属行业领域": "服饰穿搭")
    if isinstance(value, str):
        return value

    # Handle plain numeric values (e.g., "点赞数": 3648, "收藏数": 3526)
    if isinstance(value, (int, float)):
        return value

    # Handle rich text format: {"type": 1, "value": [...]}
    if isinstance(value, dict) and "value" in value:
        value = value["value"]

    # Feishu may return values as list with single element
    if isinstance(value, list) and len(value) > 0:
        first_element = value[0]
        # If first element is a dict with "text" key, extract the text value
        if isinstance(first_element, dict) and "text" in first_element:
            return first_element["text"]
        return first_element
    return default


def _extract_file_token(feishu_file_value: Any) -> Optional[str]:
    """
    Extract file_token from a Feishu file attachment field.

    Feishu file attachments are returned as:
    {
      "type": 17,
      "value": [{
        "file_token": "xxx",
        "name": "image.jpg",
        "tmp_url": "https://...",
        ...
      }]
    }

    Args:
        feishu_file_value: The value from a Feishu file field

    Returns:
        The file_token if found, None otherwise
    """
    if not feishu_file_value:
        return None

    # Handle dict with "value" key
    if isinstance(feishu_file_value, dict) and "value" in feishu_file_value:
        value_list = feishu_file_value["value"]
        if isinstance(value_list, list) and len(value_list) > 0:
            first_file = value_list[0]
            if isinstance(first_file, dict) and "file_token" in first_file:
                return first_file["file_token"]

    # Handle list directly
    if isinstance(feishu_file_value, list) and len(feishu_file_value) > 0:
        first_element = feishu_file_value[0]
        if isinstance(first_element, dict) and "file_token" in first_element:
            return first_element["file_token"]

    return None


def _extract_tmp_url(feishu_file_value: Any) -> Optional[str]:
    """
    Extract tmp_url (direct download URL) from a Feishu file attachment field.

    Args:
        feishu_file_value: The value from a Feishu file field

    Returns:
        The tmp_url if found, None otherwise
    """
    if not feishu_file_value:
        return None

    # Handle dict with "value" key
    if isinstance(feishu_file_value, dict) and "value" in feishu_file_value:
        value_list = feishu_file_value["value"]
        if isinstance(value_list, list) and len(value_list) > 0:
            first_file = value_list[0]
            if isinstance(first_file, dict) and "tmp_url" in first_file:
                return first_file["tmp_url"]

    # Handle list directly
    if isinstance(feishu_file_value, list) and len(feishu_file_value) > 0:
        first_element = feishu_file_value[0]
        if isinstance(first_element, dict) and "tmp_url" in first_element:
            return first_element["tmp_url"]

    return None


def _convert_http_to_https(url: str) -> str:
    """
    Convert HTTP URLs to HTTPS for better browser compatibility.

    This fixes mixed content issues when the frontend is served over HTTPS
    but image URLs use HTTP protocol.

    Args:
        url: The URL to convert

    Returns:
        The URL with https:// protocol if it was http://, otherwise unchanged
    """
    if url and url.startswith("http://"):
        return url.replace("http://", "https://", 1)
    return url


def _generate_image_proxy_url(file_token: str) -> str:
    """
    Generate a proxy URL for accessing Feishu images through the backend.

    Args:
        file_token: The Feishu file token

    Returns:
        The proxy URL (e.g., /api/reference/image/xxx)
    """
    return f"/api/reference/image/{file_token}"


def _get_field_int(fields: Dict[str, Any], key: str, default: int = 0) -> int:
    """Get integer field value."""
    value = _get_field_value(fields, key, default)
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def _get_field_float(fields: Dict[str, Any], key: str, default: float = 0.0) -> float:
    """Get float field value."""
    value = _get_field_value(fields, key, default)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
