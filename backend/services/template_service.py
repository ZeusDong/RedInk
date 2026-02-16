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

            result = {
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
            # 添加新字段（如果存在）
            if 'source_record_id' in template:
                result['source_record_id'] = template.get('source_record_id')
            if 'extracted_elements' in template:
                result['extracted_elements'] = template.get('extracted_elements')

            results.append(result)

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
            result = {
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
            # 添加新字段（如果存在）
            if 'source_record_id' in template:
                result['source_record_id'] = template.get('source_record_id')
            if 'extracted_elements' in template:
                result['extracted_elements'] = template.get('extracted_elements')
            return result
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

        # 添加新字段支持
        if 'source_record_id' in data:
            template['source_record_id'] = data.get('source_record_id')
            # 确保 source_records 包含 source_record_id
            source_record_id = data.get('source_record_id')
            if source_record_id and source_record_id not in template['source_records']:
                template['source_records'].append(source_record_id)

        if 'extracted_elements' in data:
            template['extracted_elements'] = data.get('extracted_elements')

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

    def extract_template_from_record(self, record_id: str) -> Dict[str, Any]:
        """
        从历史记录中提取模板元素

        Args:
            record_id: 历史记录ID

        Returns:
            提取的模板数据
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            # 1. 从 analysis.db 获取分析内容
            analysis_content, learnable_elements, record_data = self._get_analysis_data(record_id)

            if not analysis_content:
                logger.warning(f"⚠️  未找到记录 {record_id} 的分析内容，使用默认模板")
                return self._get_default_template_extraction(record_data)

            # 2. 调用 AI 提取模板
            template_data = self._ai_extract_template(
                title=record_data.get('title', '未命名'),
                industry=record_data.get('industry', '未分类'),
                analysis_content=analysis_content,
                learnable_elements=learnable_elements
            )

            logger.info(f"✅ 成功提取模板: {record_id}")
            return template_data

        except Exception as e:
            logger.error(f"❌ 提取模板失败: {e}", exc_info=True)
            # 返回默认模板
            return self._get_default_template_extraction({})

    def _get_analysis_data(self, record_id: str) -> tuple:
        """
        从 analysis.db 获取分析数据

        Returns:
            (analysis_content, learnable_elements, record_data)
        """
        import sqlite3
        import json
        from pathlib import Path

        analysis_db_path = Path(__file__).parent.parent.parent / 'analysis' / 'analysis.db'

        if not analysis_db_path.exists():
            return '', {}, {}

        try:
            conn = sqlite3.connect(str(analysis_db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 查询分析结果
            cursor.execute('''
                SELECT ar.content, ar.learnable_elements, pn.data
                FROM analysis_results ar
                INNER JOIN pending_notes pn ON ar.record_id = pn.record_id
                WHERE ar.record_id = ? AND ar.analyzed = 1
            ''', (record_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                analysis_content = row['content'] or ''
                learnable_elements = {}
                if row['learnable_elements']:
                    try:
                        learnable_elements = json.loads(row['learnable_elements'])
                    except (json.JSONDecodeError, TypeError):
                        pass
                record_data = {}
                if row['data']:
                    try:
                        record_data = json.loads(row['data'])
                    except (json.JSONDecodeError, TypeError):
                        pass
                return analysis_content, learnable_elements, record_data

            return '', {}, {}

        except Exception as e:
            logging.getLogger(__name__).warning(f"⚠️  读取分析数据失败: {e}")
            return '', {}, {}

    def _ai_extract_template(
        self,
        title: str,
        industry: str,
        analysis_content: str,
        learnable_elements: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        调用 AI 提取模板

        Returns:
            提取的模板数据
        """
        from backend.utils.text_client import get_text_chat_client
        from backend.config import Config
        from backend.prompts.recommendation_prompts import (
            format_template_extraction_prompt,
            parse_template_extraction_response
        )

        try:
            # 获取文本客户端
            text_config = Config.get_text_provider_config()
            text_client = get_text_chat_client(text_config)

            # 格式化提示词
            prompt = format_template_extraction_prompt(
                title=title,
                industry=industry,
                analysis_content=analysis_content,
                learnable_elements=learnable_elements
            )

            # 调用 AI
            response = text_client.generate_text(
                prompt=prompt,
                temperature=0.6,
                max_output_tokens=2000,
                timeout=45
            )

            # 解析响应
            template_data = parse_template_extraction_response(response)
            return template_data

        except Exception as e:
            logging.getLogger(__name__).warning(f"⚠️  AI 提取模板失败: {e}")
            return self._get_default_template_extraction({'title': title, 'industry': industry})

    def _get_default_template_extraction(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取默认的模板提取结果

        Args:
            record_data: 记录数据

        Returns:
            默认模板数据
        """
        title = record_data.get('title', '')
        industry = record_data.get('industry', '未分类')

        suggested_name = f"{industry}优质模板"
        if title:
            suggested_name = f"{title[:10]}模板"

        return {
            'suggested_name': suggested_name,
            'title_template': '',
            'structure_template': '',
            'tone_style': '',
            'cta_type': '',
            'elements': [
                {'type': 'title', 'name': '标题模板', 'description': '标题创作模式', 'selected': True},
                {'type': 'structure', 'name': '结构框架', 'description': '内容组织方式', 'selected': True},
                {'type': 'tone', 'name': '语言风格', 'description': '表达风格特点', 'selected': True},
                {'type': 'cta', 'name': '互动设计', 'description': '互动引导方式', 'selected': True}
            ]
        }


# 全局服务实例
_template_service: Optional[TemplateService] = None


def get_template_service() -> TemplateService:
    """获取模板服务实例"""
    global _template_service
    if _template_service is None:
        _template_service = TemplateService()
    return _template_service
