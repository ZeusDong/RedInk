"""
Feishu Bitable integration service.

This module provides integration with Feishu (Lark) Bitable API
for querying Xiaohongshu reference content data.

Reference implementation:
D:\cydprojects\参考项目\飞书多维表格数据读取解决方案\code\main.py
"""
import json
import logging
import os
import time
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from backend.models.reference_models import (
    BloggerInfo,
    NoteMetrics,
    ReferenceRecord,
    transform_feishu_record,
)

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path(__file__).parent.parent.parent / "reference_cache"
CACHE_DIR.mkdir(exist_ok=True)


@dataclass
class BitableParams:
    """Parsed Bitable URL parameters"""
    app_token: str
    table_id: Optional[str] = None
    view_id: Optional[str] = None


@dataclass
class FilterParams:
    """Query filter parameters"""
    keyword: Optional[str] = None
    industry: Optional[str] = None
    note_type: Optional[str] = None
    min_likes: Optional[int] = None
    min_saves: Optional[int] = None


@dataclass
class QueryResult:
    """Query result with pagination"""
    records: List[ReferenceRecord] = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    has_more: bool = False


@dataclass
class Statistics:
    """Statistics about reference records"""
    total_records: int = 0
    industry_distribution: Dict[str, int] = field(default_factory=dict)
    note_type_distribution: Dict[str, int] = field(default_factory=dict)
    avg_likes: float = 0.0
    avg_saves: float = 0.0
    avg_comments: float = 0.0


class FeishuService:
    """
    Feishu Bitable integration service (singleton pattern).

    Handles authentication, caching, and querying of Feishu Bitable data.
    """

    _instance: Optional["FeishuService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._cache: Optional[List[Dict[str, Any]]] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl: int = 3600  # Default 1 hour
        self._workspace_name: str = "default"
        self._tenant_access_token: Optional[str] = None
        self._tenant_token_expiry: Optional[datetime] = None

    def configure(self, workspace_name: str, config: Dict[str, Any]) -> None:
        """
        Configure the service with workspace credentials.

        Args:
            workspace_name: Name of the workspace
            config: Configuration dict containing app_id, app_secret, etc.
        """
        self._workspace_name = workspace_name
        self._app_id = config.get("app_id", "")
        self._app_secret = config.get("app_secret", "")
        self._user_access_token = config.get("user_access_token", "")
        self._base_url = config.get("base_url", "")
        self._cache_enabled = config.get("cache_enabled", True)
        self._cache_ttl = config.get("cache_ttl", 3600)

        # Clear cache when configuration changes
        self._cache = None
        self._cache_time = None
        # Also clear tenant access token when config changes
        self._tenant_access_token = None
        self._tenant_token_expiry = None

        logger.info(f"Feishu service configured for workspace: {workspace_name}")

    def _get_tenant_access_token(self) -> str:
        """
        Get or refresh tenant access token using app_id and app_secret.

        The tenant access token is cached and automatically refreshed when expired.
        Token expires in 2 hours, we refresh 5 minutes early to be safe.

        Returns:
            str: The tenant access token

        Raises:
            ValueError: If app_id or app_secret is not configured
            Exception: If token request fails
        """
        if not self._app_id or not self._app_secret:
            raise ValueError("app_id and app_secret are required for tenant authentication")

        # Check if we have a valid cached token (refresh 5 minutes before expiry)
        if self._tenant_access_token and self._tenant_token_expiry:
            if datetime.now() < self._tenant_token_expiry:
                logger.debug(f"Using cached tenant access token (expires at {self._tenant_token_expiry})")
                return self._tenant_access_token

        # Need to fetch a new token
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self._app_id,
            "app_secret": self._app_secret
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            logger.debug("Fetching new tenant access token from Feishu...")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("code", 0) != 0:
                raise Exception(f"Failed to get tenant access token: {result.get('msg', 'unknown error')}")

            token = result.get("tenant_access_token")
            if not token:
                raise Exception("No tenant_access_token in response")

            # Cache the token (expires in 2 hours, refresh 5 minutes early)
            self._tenant_access_token = token
            self._tenant_token_expiry = datetime.now() + timedelta(seconds=7200 - 300)  # 2h - 5min

            logger.info(f"Successfully obtained tenant access token (expires at {self._tenant_token_expiry})")
            return token

        except Exception as e:
            logger.error(f"Error getting tenant access token: {e}")
            raise

    def _parse_base_url(self) -> BitableParams:
        """
        Parse Feishu Bitable URL to extract app_token, table_id, and view_id.

        Returns:
            BitableParams: Parsed parameters

        Raises:
            ValueError: If URL cannot be parsed
        """
        if not self._base_url:
            raise ValueError("base_url is not configured")

        parsed_url = urllib.parse.urlparse(self._base_url)
        pathname = parsed_url.path
        path_parts = [p for p in pathname.split("/") if p]

        # Get app_token
        app_token = path_parts[0] if len(path_parts) > 0 else ""
        if len(path_parts) > 1:
            app_token = path_parts[1]  # For /base/{app_token} or /wiki/{node_token}

        # If it's a wiki link, we need to get the actual bitable token
        if "/wiki/" in pathname and self._app_id and self._app_secret:
            node_info = self._get_wiki_node_info(app_token)
            if node_info.get("obj_type") == "bitable":
                app_token = node_info.get("obj_token", app_token)
            else:
                logger.warning(f"Node type is not bitable, but: {node_info.get('obj_type')}")

        # Parse query parameters
        query_params = urllib.parse.parse_qs(parsed_url.query)
        view_id = query_params.get("view", [None])[0]
        table_id = query_params.get("table", [None])[0]

        # If table_id is in URL path, use it
        if len(path_parts) > 2 and not table_id:
            table_id = path_parts[2]

        result = BitableParams(
            app_token=app_token,
            table_id=table_id,
            view_id=view_id
        )
        logger.debug(f"Parsed Bitable params: app_token={app_token}, table_id={table_id}, view_id={view_id}")
        return result

    def _get_wiki_node_info(self, node_token: str) -> Dict[str, Any]:
        """
        Get wiki node information.

        Args:
            node_token: Wiki node token

        Returns:
            Dict containing node information
        """
        url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={urllib.parse.quote(node_token)}"
        # Use tenant access token for wiki API calls
        access_token = self._get_tenant_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("code", 0) != 0:
                raise Exception(f"Failed to get wiki node info: {result.get('msg', 'unknown error')}")

            if not result.get("data") or not result["data"].get("node"):
                raise Exception("No node information returned")

            return result["data"]["node"]

        except Exception as e:
            logger.error(f"Error getting wiki node info: {e}")
            raise

    def _fetch_all_records(self) -> List[Dict[str, Any]]:
        """
        Fetch all records from Feishu Bitable.

        Returns:
            List of raw Feishu records

        Raises:
            ValueError: If configuration is invalid
            Exception: If API request fails
        """
        if not self._app_id or not self._app_secret or not self._base_url:
            raise ValueError("Feishu service is not properly configured")

        bitable_params = self._parse_base_url()
        app_token = bitable_params.app_token

        # If table_id is not provided, list all tables and use the first one
        if not bitable_params.table_id:
            tables = self._list_tables(app_token)
            if not tables:
                raise ValueError("No tables found in the Bitable")
            bitable_params.table_id = tables[0].get("table_id", "")
            logger.info(f"Using first table: {tables[0].get('name', 'Unknown')}")

        if not bitable_params.table_id:
            raise ValueError("Cannot determine table_id")

        # Search records
        records = self._search_records(
            app_token,
            bitable_params.table_id,
            bitable_params.view_id
        )

        return records

    def _list_tables(self, app_token: str, page_size: int = 20) -> List[Dict[str, Any]]:
        """
        List all tables in the Bitable.

        Args:
            app_token: Bitable app token
            page_size: Page size for pagination

        Returns:
            List of table information
        """
        tables = []
        page_token = None

        while True:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables"
            params = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token

            # Get tenant access token for authentication
            access_token = self._get_tenant_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=utf-8"
            }

            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                result = response.json()

                if result.get("code", 0) != 0:
                    raise Exception(f"Failed to list tables: {result.get('msg', 'unknown error')}")

                if "data" in result and "items" in result["data"]:
                    tables.extend(result["data"]["items"])

                if result["data"].get("has_more", False):
                    page_token = result["data"].get("page_token")
                    if not page_token:
                        break
                else:
                    break

            except Exception as e:
                logger.error(f"Error listing tables: {e}")
                raise

        return tables

    def _search_records(
        self,
        app_token: str,
        table_id: str,
        view_id: Optional[str] = None,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search records from Feishu Bitable.

        Args:
            app_token: Bitable app token
            table_id: Table ID
            view_id: Optional view ID
            page_size: Page size (max 500)

        Returns:
            List of raw records
        """
        records = []
        page_token = None
        page_size = min(page_size, 500)

        while True:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search"
            params = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token

            # Get tenant access token for authentication
            access_token = self._get_tenant_access_token()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=utf-8"
            }

            payload = {}
            if view_id:
                payload["view_id"] = view_id
            # Empty filter to get all records
            payload["filter"] = {
                "conjunction": "and",
                "conditions": []
            }

            try:
                response = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()

                if result.get("code", 0) != 0:
                    raise Exception(f"Failed to search records: {result.get('msg', 'unknown error')}")

                if "data" in result and "items" in result["data"]:
                    records.extend(result["data"]["items"])
                    logger.debug(f"Fetched {len(records)} records, total: {result['data'].get('total', 'unknown')}")

                if result["data"].get("has_more", False):
                    page_token = result["data"].get("page_token")
                    if not page_token:
                        break
                else:
                    break

            except Exception as e:
                logger.error(f"Error searching records: {e}")
                raise

        return records

    def _load_cache(self) -> Optional[List[Dict[str, Any]]]:
        """
        Load cached records from file.

        Returns:
            Cached records or None if cache is invalid
        """
        cache_file = CACHE_DIR / f"{self._workspace_name}_cache.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            cache_time = datetime.fromisoformat(cache_data.get("cached_at", ""))
            expiry_time = cache_time + timedelta(seconds=self._cache_ttl)

            if datetime.now() > expiry_time:
                logger.info("Cache has expired")
                return None

            logger.info(f"Loaded cache from {cache_file} ({len(cache_data.get('records', []))} records)")
            return cache_data.get("records", [])

        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return None

    def _save_cache(self, records: List[Dict[str, Any]]) -> None:
        """
        Save records to cache file.

        Args:
            records: Records to cache
        """
        cache_file = CACHE_DIR / f"{self._workspace_name}_cache.json"

        try:
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "workspace": self._workspace_name,
                "total": len(records),
                "records": records
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(records)} records to cache: {cache_file}")

        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def _apply_filters(
        self,
        records: List[ReferenceRecord],
        filters: FilterParams
    ) -> List[ReferenceRecord]:
        """
        Apply filter conditions to records.

        Args:
            records: List of records to filter
            filters: Filter parameters

        Returns:
            Filtered list of records
        """
        filtered = records

        # Keyword search (search in title, body, tags, blogger name)
        if filters.keyword:
            keyword_lower = filters.keyword.lower()
            filtered = [
                r for r in filtered
                if keyword_lower in r.title.lower()
                or keyword_lower in r.body.lower()
                or keyword_lower in r.keyword.lower()
                or any(keyword_lower in tag.lower() for tag in r.tags)
                or keyword_lower in r.blogger.nickname.lower()
            ]

        # Industry filter
        if filters.industry:
            filtered = [r for r in filtered if r.industry == filters.industry]

        # Note type filter
        if filters.note_type:
            filtered = [r for r in filtered if r.note_type == filters.note_type]

        # Minimum likes filter
        if filters.min_likes is not None:
            filtered = [r for r in filtered if r.metrics.likes >= filters.min_likes]

        # Minimum saves filter
        if filters.min_saves is not None:
            filtered = [r for r in filtered if r.metrics.saves >= filters.min_saves]

        logger.debug(f"Filtered records: {len(records)} -> {len(filtered)}")
        return filtered

    def _apply_sort(
        self,
        records: List[ReferenceRecord],
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[ReferenceRecord]:
        """
        Apply sorting to records.

        Args:
            records: List of records to sort
            sort_by: Field to sort by
            sort_order: "asc" or "desc"

        Returns:
            Sorted list of records
        """
        reverse = sort_order.lower() == "desc"

        if sort_by == "created_at":
            records.sort(key=lambda r: r.created_at or datetime.min, reverse=reverse)
        elif sort_by == "likes":
            records.sort(key=lambda r: r.metrics.likes, reverse=reverse)
        elif sort_by == "saves":
            records.sort(key=lambda r: r.metrics.saves, reverse=reverse)
        elif sort_by == "comments":
            records.sort(key=lambda r: r.metrics.comments, reverse=reverse)
        elif sort_by == "total_engagement":
            records.sort(key=lambda r: r.metrics.total_engagement, reverse=reverse)
        elif sort_by == "save_ratio":
            records.sort(key=lambda r: r.metrics.save_ratio, reverse=reverse)

        return records

    def list_records(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        industry: Optional[str] = None,
        note_type: Optional[str] = None,
        min_likes: Optional[int] = None,
        min_saves: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> QueryResult:
        """
        Query records with pagination, filtering, and sorting.

        Args:
            page: Page number (1-indexed)
            page_size: Number of records per page
            keyword: Search keyword
            industry: Industry filter
            note_type: Note type filter
            min_likes: Minimum likes filter
            min_saves: Minimum saves filter
            sort_by: Sort field
            sort_order: Sort order ("asc" or "desc")

        Returns:
            QueryResult containing filtered and paginated records
        """
        # Get records (from cache or API)
        if self._cache_enabled and self._cache is not None:
            if self._cache_time and (datetime.now() - self._cache_time).total_seconds() < self._cache_ttl:
                raw_records = self._cache
            else:
                raw_records = self._fetch_all_records()
                self._cache = raw_records
                self._cache_time = datetime.now()
                if self._cache_enabled:
                    self._save_cache(raw_records)
        elif self._cache_enabled:
            # Try loading from file cache
            raw_records = self._load_cache()
            if raw_records is None:
                raw_records = self._fetch_all_records()
                self._cache = raw_records
                self._cache_time = datetime.now()
                self._save_cache(raw_records)
            else:
                self._cache = raw_records
                self._cache_time = datetime.now()
        else:
            raw_records = self._fetch_all_records()

        # Transform to ReferenceRecord
        records = [transform_feishu_record(r) for r in raw_records]

        # Apply filters
        filters = FilterParams(
            keyword=keyword,
            industry=industry,
            note_type=note_type,
            min_likes=min_likes,
            min_saves=min_saves
        )
        filtered = self._apply_filters(records, filters)

        # Apply sorting
        sorted_records = self._apply_sort(filtered, sort_by, sort_order)

        # Pagination
        total = len(sorted_records)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_records = sorted_records[start_idx:end_idx]

        return QueryResult(
            records=page_records,
            total=total,
            page=page,
            page_size=page_size,
            has_more=end_idx < total
        )

    def get_record(self, record_id: str) -> Optional[ReferenceRecord]:
        """
        Get a single record by ID.

        Args:
            record_id: Record ID

        Returns:
            ReferenceRecord or None if not found
        """
        result = self.list_records(page=1, page_size=1000)  # Get all records
        for record in result.records:
            if record.record_id == record_id:
                return record
        return None

    def get_statistics(self) -> Statistics:
        """
        Get statistics about all records.

        Returns:
            Statistics object
        """
        result = self.list_records(page=1, page_size=10000)  # Get all records
        records = result.records

        if not records:
            return Statistics()

        # Industry distribution
        industry_dist: Dict[str, int] = {}
        for record in records:
            industry = record.industry or "Unknown"
            industry_dist[industry] = industry_dist.get(industry, 0) + 1

        # Note type distribution
        type_dist: Dict[str, int] = {}
        for record in records:
            note_type = record.note_type or "Unknown"
            type_dist[note_type] = type_dist.get(note_type, 0) + 1

        # Average metrics
        total_likes = sum(r.metrics.likes for r in records)
        total_saves = sum(r.metrics.saves for r in records)
        total_comments = sum(r.metrics.comments for r in records)
        count = len(records)

        return Statistics(
            total_records=count,
            industry_distribution=industry_dist,
            note_type_distribution=type_dist,
            avg_likes=total_likes / count if count > 0 else 0,
            avg_saves=total_saves / count if count > 0 else 0,
            avg_comments=total_comments / count if count > 0 else 0,
        )

    def sync_data(self) -> Dict[str, Any]:
        """
        Force sync data from Feishu (clear cache and reload).

        Returns:
            Dict with sync status and record count
        """
        logger.info("Forcing data sync from Feishu...")
        self._cache = None
        self._cache_time = None

        # Clear file cache
        cache_file = CACHE_DIR / f"{self._workspace_name}_cache.json"
        if cache_file.exists():
            cache_file.unlink()
            logger.info(f"Deleted cache file: {cache_file}")

        # Fetch new data
        raw_records = self._fetch_all_records()
        self._cache = raw_records
        self._cache_time = datetime.now()

        if self._cache_enabled:
            self._save_cache(raw_records)

        return {
            "success": True,
            "message": f"Synced {len(raw_records)} records from Feishu",
            "count": len(raw_records),
            "synced_at": self._cache_time.isoformat() if self._cache_time else None,
        }

    def test_connection(self, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Test Feishu connection and configuration.

        Args:
            config: Optional config to test (uses current config if None)

        Returns:
            Dict with test result
        """
        test_config = config or {
            "app_id": self._app_id,
            "app_secret": self._app_secret,
            "user_access_token": self._user_access_token,
            "base_url": self._base_url,
        }

        try:
            # Validate required fields
            if not test_config.get("app_id"):
                return {"success": False, "error": "app_id is required"}
            if not test_config.get("app_secret"):
                return {"success": False, "error": "app_secret is required"}
            if not test_config.get("base_url"):
                return {"success": False, "error": "base_url is required"}

            # Temporarily configure with test config
            old_config = {
                "_app_id": getattr(self, "_app_id", None),
                "_app_secret": getattr(self, "_app_secret", None),
                "_user_access_token": getattr(self, "_user_access_token", None),
                "_base_url": getattr(self, "_base_url", None),
            }

            self.configure("test", test_config)

            # Try to parse base URL
            bitable_params = self._parse_base_url()

            # Try to list tables
            tables = self._list_tables(bitable_params.app_token)
            table_names = [t.get("name", "Unknown") for t in tables]

            result = {
                "success": True,
                "message": f"Connection successful! Found {len(tables)} table(s)",
                "tables": table_names,
                "app_token": bitable_params.app_token,
            }

            # Restore old config
            for key, value in old_config.items():
                if value is not None:
                    setattr(self, key[1:], value)

            return result

        except Exception as e:
            logger.error(f"Feishu connection test failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance getter
def get_feishu_service() -> FeishuService:
    """Get the singleton FeishuService instance."""
    return FeishuService()
