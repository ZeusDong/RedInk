"""
推荐系统 AI 提示词

用于从已分析的笔记中提炼可学习的元素和推荐理由
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def format_insights_extraction_prompt(
    topic: str,
    analysis_content: str,
    record: Dict[str, Any]
) -> str:
    """
    格式化 AI 提炼提示词

    Args:
        topic: 用户搜索的主题
        analysis_content: AI 分析结果（7层拆解内容）
        record: 笔记数据字典

    Returns:
        完整的 AI 提示词
    """
    title = record.get('title', '')
    industry = record.get('industry', '')
    metrics = record.get('metrics', {})
    total_engagement = metrics.get('total_engagement', 0)

    prompt = f"""你是一位专业的小红书内容策略专家，擅长从优质笔记中提炼可复用的创作元素。

## 用户搜索主题
{topic}

## 笔记基本信息
- 标题：{title}
- 行业：{industry}
- 总互动量：{total_engagement}

## AI 深度分析（7层拆解）
{analysis_content}

## 任务要求
请基于以上分析内容，提炼以下信息：

### 1. 推荐理由（recommend_reasons）
最多3条，每条不超过30字，必须是用户可读的自然语言，说明为什么这个笔记值得学习。
考虑维度：
- 爆款逻辑：为什么能火？
- 内容价值：用户获得什么？
- 创作技巧：有哪些亮点？

### 2. 可学习元素（learnable_elements）
提炼4个维度的可复用元素，每个不超过15字：

**a) 钩子类型（hook）**
开头用什么方式吸引注意？例如：
- 数字悬念："3个技巧..."
- 痛点共鸣："你是不是也..."
- 利益前置："教你省钱..."

**b) 结构框架（structure）**
内容如何组织？例如：
- 问题-解决方案
- 对比测评
- 分步骤教程

**c) 语言风格（tone）**
表达特点？例如：
- 姐妹聊天式
- 专业干货型
- 搞笑轻松风

**d) 互动设计（cta）**
如何引导互动？例如：
- "你觉得呢？评论区见"
- "点赞收藏不迷路"
- "转发给你最爱的人"

## 输出格式
请严格按照以下 JSON 格式输出（不要添加任何其他文字）：

```json
{{
  "recommend_reasons": [
    "推荐理由1",
    "推荐理由2",
    "推荐理由3"
  ],
  "learnable_elements": {{
    "hook": "钩子类型",
    "structure": "结构框架",
    "tone": "语言风格",
    "cta": "互动设计"
  }}
}}
```

## 注意事项
1. 必须基于分析结果，不要编造
2. 语言要简洁、准确、可操作
3. JSON 必须有效且符合格式
4. 每个元素都要具体，不要用"很好"、"不错"等空泛词汇
"""

    return prompt


def parse_insights_response(response: str) -> Dict[str, Any]:
    """
    解析 AI 返回的提炼结果

    Args:
        response: AI 返回的文本

    Returns:
        解析后的结构化数据
    """
    import json
    import re

    # 尝试直接解析 JSON
    try:
        # 提取 JSON 代码块
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试找纯 JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response

        data = json.loads(json_str)

        # 验证必需字段
        if 'recommend_reasons' not in data or 'learnable_elements' not in data:
            raise ValueError("Missing required fields in AI response")

        return {
            'recommend_reasons': data['recommend_reasons'][:3],  # 最多3条
            'learnable_elements': data['learnable_elements'],
            'extracted_at': None  # 将在保存时设置
        }

    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse AI insights response: {e}, using fallback")

        # 降级：规则提取
        return fallback_insights_extraction(response)


def fallback_insights_extraction(response: str) -> Dict[str, Any]:
    """
    降级策略：从非结构化文本中提取洞察

    Args:
        response: AI 返回的文本

    Returns:
        结构化数据（可能不完整）
    """
    import re

    reasons = []
    elements = {'hook': '', 'structure': '', 'tone': '', 'cta': ''}

    # 尝试提取推荐理由
    reason_patterns = [
        r'推荐理由\d*[：:]\s*([^\n]+)',
        r'recommend_reasons?\d*[：:]\s*([^\n]+)',
        r'为什么[：:]\s*([^\n]+)',
    ]
    for pattern in reason_patterns:
        matches = re.findall(pattern, response)
        for match in matches:
            reason = match.strip()[:30]  # 限制长度
            if reason and len(reasons) < 3:
                reasons.append(reason)

    # 尝试提取钩子
    hook_patterns = [
        r'钩子\d*[：:]\s*([^\n]+)',
        r'hook\d*[：:]\s*([^\n]+)',
    ]
    for pattern in hook_patterns:
        match = re.search(pattern, response)
        if match:
            elements['hook'] = match.group(1).strip()[:15]
            break

    # 尝试提取结构
    structure_patterns = [
        r'结构\d*[：:]\s*([^\n]+)',
        r'structure\d*[：:]\s*([^\n]+)',
    ]
    for pattern in structure_patterns:
        match = re.search(pattern, response)
        if match:
            elements['structure'] = match.group(1).strip()[:15]
            break

    # 尝试提取风格
    tone_patterns = [
        r'风格\d*[：:]\s*([^\n]+)',
        r'tone\d*[：:]\s*([^\n]+)',
    ]
    for pattern in tone_patterns:
        match = re.search(pattern, response)
        if match:
            elements['tone'] = match.group(1).strip()[:15]
            break

    # 尝试提取互动设计
    cta_patterns = [
        r'互动\d*[：:]\s*([^\n]+)',
        r'cta\d*[：:]\s*([^\n]+)',
    ]
    for pattern in cta_patterns:
        match = re.search(pattern, response)
        if match:
            elements['cta'] = match.group(1).strip()[:15]
            break

    # 如果没有提取到推荐理由，使用通用理由
    if not reasons:
        reasons = [
            "内容质量高，结构清晰",
            "数据表现优秀，值得学习"
        ]

    return {
        'recommend_reasons': reasons,
        'learnable_elements': elements,
        'extracted_at': None
    }


def format_match_score_display(score: float) -> str:
    """
    格式化匹配度显示文本

    Args:
        score: 匹配分数 0-1

    Returns:
        显示文本
    """
    if score >= 0.7:
        return "🔥 高度匹配"
    elif score >= 0.4:
        return "📌 相关推荐"
    elif score >= 0.3:
        return "💡 可能相关"
    else:
        return "📝 相关参考"


def calculate_match_level(score: float) -> str:
    """
    计算匹配等级

    Args:
        score: 匹配分数 0-1

    Returns:
        匹配等级: high | medium | low
    """
    if score >= 0.7:
        return 'high'
    elif score >= 0.4:
        return 'medium'
    else:
        return 'low'
