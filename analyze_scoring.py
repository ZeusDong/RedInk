#!/usr/bin/env python3
"""分析评分逻辑问题"""

def calculate_final_score(topic_relevance, audience_match, style_fit, performance_bonus):
    """计算最终得分（复制自 recommendation_prompts.py）"""
    return round(
        topic_relevance * 0.4 +
        audience_match * 0.3 +
        style_fit * 0.2 +
        performance_bonus * 0.1,
        2
    )

print("=" * 80)
print("评分逻辑分析")
print("=" * 80)
print()

print("场景 1: 完美匹配（各项满分）")
print(f"  主题相关度: 10, 目标用户匹配: 10, 内容风格适配: 10, 数据表现加分: 5")
print(f"  最终得分: {calculate_final_score(10, 10, 10, 5)}")
print()

print("场景 2: 标题包含搜索词，其他一般（很可能的情况）")
print(f"  主题相关度: 10, 目标用户匹配: 5, 内容风格适配: 5, 数据表现加分: 3")
print(f"  最终得分: {calculate_final_score(10, 5, 5, 3)}")
print(f"  归一化分数: {calculate_final_score(10, 5, 5, 3) / 10}")
print(f"  是否高度匹配: {calculate_final_score(10, 5, 5, 3) >= 7.0}")
print()

print("场景 3: 刚好达到 7.0 分需要什么？")
print("  需要: 主题相关度 10 + 目标用户匹配 7 + 内容风格适配 7 + 数据表现加分 4")
print(f"  最终得分: {calculate_final_score(10, 7, 7, 4)}")
print()

print("场景 4: 如果数据表现加分也是 0-10 分制")
def calculate_final_score_10(topic_relevance, audience_match, style_fit, performance_bonus):
    return round(
        topic_relevance * 0.4 +
        audience_match * 0.3 +
        style_fit * 0.2 +
        performance_bonus * 0.1,
        2
    )
print(f"  主题相关度: 10, 目标用户匹配: 5, 内容风格适配: 5, 数据表现加分: 6")
print(f"  最终得分: {calculate_final_score_10(10, 5, 5, 6)}")
print()

print("=" * 80)
print("问题总结：")
print("1. 数据表现加分只有 0-5 分，拉低了总分上限")
print("2. 要达到 7.0 分的高度匹配阈值太难了")
print("3. 解决方案：要么把数据表现加分改成 0-10 分，要么降低高度匹配阈值")
print("=" * 80)
