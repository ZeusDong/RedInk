"""
模板组管理服务

功能：
- 按笔记分组管理创作技巧
- 模板组的创建、读取、删除
- 单个技巧的删除和使用计数
"""

import logging
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TemplateGroupService:
    """模板组管理服务"""

    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化模板组服务

        Args:
            storage_path: 模板组存储路径，默认使用 data/template_groups
        """
        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / 'data' / 'template_groups'

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.groups: Dict[str, Any] = {}
        self._load_groups()

    def _load_groups(self):
        """加载所有模板组数据"""
        try:
            group_files = list(self.storage_path.glob('*.json'))
            for group_file in group_files:
                try:
                    with open(group_file, 'r', encoding='utf-8') as f:
                        group = json.load(f)
                        self.groups[group['group_id']] = group
                except Exception as e:
                    logger.error(f"❌ 加载模板组失败 {group_file}: {e}")
            logger.info(f"✅ 加载了 {len(self.groups)} 个模板组")
        except Exception as e:
            logger.error(f"❌ 加载模板组目录失败: {e}")

    def _save_group(self, group: Dict[str, Any]):
        """保存模板组到文件"""
        try:
            group_id = group['group_id']
            file_path = self.storage_path / f'{group_id}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(group, f, ensure_ascii=False, indent=2)
            logger.debug(f"✅ 保存模板组: {group_id}")
        except Exception as e:
            logger.error(f"❌ 保存模板组失败: {e}")
            raise

    def list_groups(
        self,
        element_type: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = 'saved_at'
    ) -> List[Dict[str, Any]]:
        """
        获取模板组列表

        Args:
            element_type: 技巧类型筛选 (title|structure|tone|cta)
            search: 搜索关键词
            sort_by: 排序字段 (saved_at|usage_count|match_score)

        Returns:
            模板组列表
        """
        results = []

        for group in self.groups.values():
            # 类型筛选：只返回包含该类型技巧的分组
            if element_type:
                has_type = any(e['type'] == element_type for e in group.get('elements', []))
                if not has_type:
                    continue

            # 搜索筛选
            if search:
                search_lower = search.lower()
                title_match = search_lower in group.get('source_title', '').lower()
                industry_match = search_lower in group.get('source_industry', '').lower()
                elements_match = any(
                    search_lower in e.get('name', '').lower() or
                    search_lower in e.get('description', '').lower()
                    for e in group.get('elements', [])
                )
                if not (title_match or industry_match or elements_match):
                    continue

            results.append(group)

        # 排序
        if sort_by == 'usage_count':
            # 按分组内所有技巧的总使用次数排序
            results.sort(
                key=lambda g: sum(e.get('usage_count', 0) for e in g.get('elements', [])),
                reverse=True
            )
        elif sort_by == 'match_score':
            results.sort(
                key=lambda g: g.get('match_score', 0),
                reverse=True
            )
        else:  # saved_at
            results.sort(
                key=lambda g: g.get('saved_at', ''),
                reverse=True
            )

        return results

    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个模板组

        Args:
            group_id: 模板组ID

        Returns:
            模板组数据或None
        """
        return self.groups.get(group_id)

    def create_group(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新模板组

        Args:
            data: 模板组数据

        Returns:
            创建的模板组
        """
        group_id = str(uuid.uuid4())

        # 构建元素列表
        elements = []
        for elem_data in data.get('elements', []):
            element = {
                'id': str(uuid.uuid4()),
                'type': elem_data.get('type', 'title'),
                'name': elem_data.get('name', ''),
                'description': elem_data.get('description', ''),
                'content': elem_data.get('content', ''),
                'examples': elem_data.get('examples', []),
                'usage_count': 0,
                'created_at': datetime.now().isoformat()
            }
            elements.append(element)

        group = {
            'group_id': group_id,
            'source_record_id': data.get('source_record_id', ''),
            'source_title': data.get('source_title', ''),
            'source_industry': data.get('source_industry'),
            'source_cover': data.get('source_cover'),
            'match_score': data.get('match_score'),
            'saved_at': datetime.now().isoformat(),
            'elements': elements
        }

        self.groups[group_id] = group
        self._save_group(group)

        logger.info(f"✅ 创建模板组: {group_id}")
        return group

    def delete_group(self, group_id: str) -> bool:
        """
        删除模板组

        Args:
            group_id: 模板组ID

        Returns:
            是否成功
        """
        if group_id in self.groups:
            del self.groups[group_id]

            # 删除文件
            file_path = self.storage_path / f'{group_id}.json'
            if file_path.exists():
                file_path.unlink()

            logger.info(f"✅ 删除模板组: {group_id}")
            return True

        logger.warning(f"⚠️  模板组不存在: {group_id}")
        return False

    def delete_element(self, group_id: str, element_id: str) -> bool:
        """
        删除单个技巧

        Args:
            group_id: 模板组ID
            element_id: 技巧ID

        Returns:
            是否成功
        """
        group = self.groups.get(group_id)
        if not group:
            logger.warning(f"⚠️  模板组不存在: {group_id}")
            return False

        elements = group.get('elements', [])
        element_index = next((i for i, e in enumerate(elements) if e['id'] == element_id), None)

        if element_index is None:
            logger.warning(f"⚠️  技巧不存在: {element_id}")
            return False

        # 删除技巧
        elements.pop(element_index)
        self._save_group(group)

        logger.info(f"✅ 删除技巧: {element_id} from group {group_id}")
        return True

    def increment_usage(self, group_id: str, element_id: str) -> bool:
        """
        增加技巧使用次数

        Args:
            group_id: 模板组ID
            element_id: 技巧ID

        Returns:
            是否成功
        """
        group = self.groups.get(group_id)
        if not group:
            logger.warning(f"⚠️  模板组不存在: {group_id}")
            return False

        elements = group.get('elements', [])
        element = next((e for e in elements if e['id'] == element_id), None)

        if not element:
            logger.warning(f"⚠️  技巧不存在: {element_id}")
            return False

        # 更新使用次数
        element['usage_count'] = element.get('usage_count', 0) + 1
        self._save_group(group)

        logger.info(f"✅ 技巧使用次数+1: {element_id}")
        return True

    def update_group(self, group_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新模板组基本信息

        Args:
            group_id: 模板组ID
            data: 要更新的字段数据

        Returns:
            更新后的模板组或None
        """
        group = self.groups.get(group_id)
        if not group:
            logger.warning(f"⚠️  模板组不存在: {group_id}")
            return None

        # 更新字段
        if 'source_title' in data:
            group['source_title'] = data['source_title']
        if 'source_industry' in data:
            group['source_industry'] = data['source_industry']
        if 'source_cover' in data:
            group['source_cover'] = data['source_cover']

        self._save_group(group)
        logger.info(f"✅ 更新模板组: {group_id}")
        return group

    def update_element(self, group_id: str, element_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新单个技巧

        Args:
            group_id: 模板组ID
            element_id: 技巧ID
            data: 要更新的字段数据

        Returns:
            更新后的技巧或None
        """
        group = self.groups.get(group_id)
        if not group:
            logger.warning(f"⚠️  模板组不存在: {group_id}")
            return None

        element = next((e for e in group['elements'] if e['id'] == element_id), None)
        if not element:
            logger.warning(f"⚠️  技巧不存在: {element_id}")
            return None

        # 更新字段
        updatable_fields = ['name', 'description', 'content', 'examples']
        for field in updatable_fields:
            if field in data:
                element[field] = data[field]

        element['updated_at'] = datetime.now().isoformat()
        self._save_group(group)
        logger.info(f"✅ 更新技巧: {element_id}")
        return element

    def add_element(self, group_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        添加新技巧到分组

        Args:
            group_id: 模板组ID
            data: 技巧数据

        Returns:
            新增的技巧或None
        """
        group = self.groups.get(group_id)
        if not group:
            logger.warning(f"⚠️  模板组不存在: {group_id}")
            return None

        element = {
            'id': str(uuid.uuid4()),
            'type': data.get('type', 'title'),
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'content': data.get('content', ''),
            'examples': data.get('examples', []),
            'usage_count': 0,
            'created_at': datetime.now().isoformat()
        }

        group['elements'].append(element)
        self._save_group(group)
        logger.info(f"✅ 添加新技巧: {element['id']} to group {group_id}")
        return element


# 全局服务实例
_template_group_service: Optional[TemplateGroupService] = None


def get_template_group_service() -> TemplateGroupService:
    """获取模板组服务实例"""
    global _template_group_service
    if _template_group_service is None:
        _template_group_service = TemplateGroupService()
    return _template_group_service
