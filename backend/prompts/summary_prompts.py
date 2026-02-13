"""
AI Summary Prompts Module

Provides prompt templates for generating AI summaries of analyzed content.
"""

from typing import List

# ==================== Summary Generation Prompt ====================

SUMMARY_PROMPT = """【背景】
我正在研究 {industry} 的爆款内容规律。
我已经完成了 {report_count} 篇爆款的深度拆解，现在需要你扮演一个"数据分析师+内容策略师"的角色，帮我从这些案例中提炼出可执行的创作方法论。

【输入材料】
{reports_text}

【分析任务】
请按以下步骤进行分析：

**第一步：数据清洗**
- 统计每个维度（钩子、选题、结构等）中，出现频率最高的 3 种手法。
- 标注出"低粉爆款"（粉丝量 < 1W 但数据表现优异）的特殊规律。

**第二步：因果推理**
- 分析"高互动数据"（点赞/收藏/评论）与哪些维度的相关性最强？
- 哪些手法是"必要条件"（所有爆款都有），哪些是"充分条件"（有了就容易火）？

**第三步：模式分类**
- 根据分析结果，将这些爆款分为 2-3 种"爆款类型"（如：情绪共鸣型、干货价值型、争议话题型）。
- 每种类型给出一个"典型案例编号"和"核心特征描述"。

**第四步：武器化输出**
为每种爆款类型，输出一套"创作 SOP"，包含：
1. 选题方向（3个具体角度）
2. 开头模板（2-3 个可直接套用的句式）
3. 结构框架（如：痛点-方案-行动）
4. 情绪调动策略（在哪个节点埋什么钩子）
5. 互动引导话术（结尾 CTA 怎么写）

【输出格式】
- 第一步和第二步用表格呈现。
- 第三步用分类卡片（每个类型一个独立板块）。
- 第四步用"可复制粘贴"的模板形式。

请开始分析："""


def format_summary_prompt(
    industry: str,
    analysis_reports: List[str]
) -> str:
    """
    格式化AI总结提示词

    Args:
        industry: 行业名称
        analysis_reports: 所有分析报告的内容列表

    Returns:
        格式化后的提示词
    """
    reports_text = "\n\n---\n\n".join([
        f"## 案例 {i+1}\n{report}"
        for i, report in enumerate(analysis_reports)
    ])

    return SUMMARY_PROMPT.format(
        industry=industry,
        report_count=len(analysis_reports),
        reports_text=reports_text
    )
