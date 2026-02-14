"""
模板管理服务

功能：
- 模板的创建、读取、更新、删除
- 模板应用生成内容
"""

import logging
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TemplateService:
    """模板管理服务"""

    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化模板服务

        Args:
            storage_path: 模板存储路径，默认使用 data/templates
        """
        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / 'data' / 'templates'

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, Any] = {}
        self._load_templates()

    def _load_templates(self):
        """加载模板数据"""
        try:
            template_files = list(self.storage_path.glob('*.json'))
            for template_file in template_files:
                try:
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                        self.templates[template['id']] = template
                except Exception as e:
                    logger.error(f"❌ 加载模板失败 {template_file}: {e}")
            logger.info(f"✅ 加载了 {len(self.templates)} 个模板")
        except Exception as e:
            logger.error(f"❌ 加载模板目录失败: {e}")

    def _save_template(self, template: Dict[str, Any]):
        """保存模板到文件"""
        try:
            template_id = template['id']
            file_path = self.storage_path / f'{template_id}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            logger.debug(f"✅ 保存模板: {template_id}")
        except Exception as e:
            logger.error(f"❌ 保存模板失败: {e}")
            raise

    def list_templates(
        self,
        template_type: Optional[str] = None,
        industry: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取模板列表

        Args:
            template_type: 模板类型筛选
            industry: 行业筛选

        Returns:
            模板列表
        """
        results = []

        for template in self.templates.values():
            # 类型筛选
            if template_type and template.get('type') != template_type:
                continue

            # 行业筛选
            if industry and template.get('industry') != industry:
                continue

            results.append({
                'id': template.get('id'),
                'type': template.get('type'),
                'name': template.get('name'),
                'industry': template.get('industry'),
                'pattern': template.get('pattern'),
                'variables': template.get('variables', []),
                'usage_count': template.get('usage_count', 0),
                'description': template.get('description'),
                'examples': template.get('examples', []),
                'source_records': template.get('source_records', [])
            })

        # 按使用次数排序
        results.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
        return results

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个模板

        Args:
            template_id: 模板ID

        Returns:
            模板数据或None
        """
        template = self.templates.get(template_id)
        if template:
            return {
                'id': template.get('id'),
                'type': template.get('type'),
                'name': template.get('name'),
                'industry': template.get('industry'),
                'pattern': template.get('pattern'),
                'variables': template.get('variables', []),
                'usage_count': template.get('usage_count', 0),
                'description': template.get('description'),
                'examples': template.get('examples', []),
                'source_records': template.get('source_records', [])
            }
        return None

    def create_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新模板

        Args:
            data: 模板数据

        Returns:
            创建的模板
        """
        template_id = str(uuid.uuid4())

        template = {
            'id': template_id,
            'type': data.get('type', 'title'),
            'name': data.get('name', ''),
            'industry': data.get('industry'),
            'pattern': data.get('pattern', ''),
            'variables': data.get('variables', []),
            'source_records': data.get('source_records', []),
            'usage_count': 0,
            'description': data.get('description'),
            'examples': data.get('examples', []),
            'created_at': datetime.now().isoformat()
        }

        self.templates[template_id] = template
        self._save_template(template)

        logger.info(f"✅ 创建模板: {template_id}")
        return self.get_template(template_id)

    def apply_template(self, template_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用模板生成内容

        Args:
            template_id: 模板ID
            context: 应用上下文 {topic, industry等}

        Returns:
            生成的结果
        """
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")

        # 更新使用次数
        template['usage_count'] = template.get('usage_count', 0) + 1
        self._save_template(template)

        topic = context.get('topic', '')
        industry = context.get('industry', template.get('industry'))

        result = {
            'template_id': template_id,
            'template_name': template.get('name'),
            'applied_at': datetime.now().isoformat()
        }

        template_type = template.get('type')

        if template_type == 'title':
            result['title'] = self._apply_title_template(template, topic)
        elif template_type == 'structure':
            result['outline'] = self._apply_structure_template(template, topic)
        elif template_type == 'visual':
            result['visual_guide'] = self._apply_visual_template(template, topic)
        else:
            result['content'] = f"基于模板 {template.get('name')} 生成的内容"

        logger.info(f"✅ 应用模板: {template_id}, type: {template_type}")
        return result

    def _apply_title_template(self, template: Dict[str, Any], topic: str) -> str:
        """应用标题模板"""
        result = template.get('pattern', '')
        # 简单变量替换
        variables = template.get('variables', [])
        for var in variables:
            if var == '{主题}':
                result = result.replace(var, topic)
            elif var == '{数字}':
                result = result.replace(var, '3')
            elif var == '{季节}':
                seasons = ['春', '夏', '秋', '冬']
                result = result.replace(var, seasons[0] if seasons else '春')

        return result

    def _apply_structure_template(self, template: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """应用结构模板"""
        return {
            'title': f'{topic} - 使用{template.get("name")}',
            'structure': template.get('pattern'),
            'pages': self._generate_pages_from_structure(template, topic)
        }

    def _apply_visual_template(self, template: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """应用视觉模板"""
        return {
            'style': template.get('pattern'),
            'color_scheme': template.get('variables', {}).get('colors', '默认配色'),
            'composition': template.get('variables', {}).get('composition', '标准构图')
        }

    def _generate_pages_from_structure(self, template: Dict[str, Any], topic: str) -> List[Dict[str, Any]]:
        """从模板生成页面"""
        # 简化实现
        return [
            {
                'page_number': 1,
                'content': f'{topic}相关内容...'
            }
        ]

    def delete_template(self, template_id: str) -> bool:
        """
        删除模板

        Args:
            template_id: 模板ID

        Returns:
            是否成功
        """
        if template_id in self.templates:
            del self.templates[template_id]

            # 删除文件
            file_path = self.storage_path / f'{template_id}.json'
            if file_path.exists():
                file_path.unlink()

            logger.info(f"✅ 删除模板: {template_id}")
            return True

        logger.warning(f"⚠️  模板不存在: {template_id}")
        return False


# 全局服务实例
_template_service: Optional[TemplateService] = None


def get_template_service() -> TemplateService:
    """获取模板服务实例"""
    global _template_service
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service
