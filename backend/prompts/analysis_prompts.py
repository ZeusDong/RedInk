"""
AI Analysis Prompts Module

Provides prompt templates for content analysis including:
- Visual description generation (image analysis)
- Full content analysis (text-based multi-dimensional breakdown)
"""

# ==================== Visual Analysis Prompts ====================

IMAGE_ANALYSIS_PROMPT = """【指令】
你现在是一位资深的平面设计师和视觉营销专家。请从"点击率（CTR）"的角度，深度分析这张{image_type}。

请不要只描述画面，要输出以下结构化数据：

**构图策略：**
（例如：三分法、中心聚焦、左右对比）

**色彩心理：**
（主色调是什么？强调色是什么？为什么这样配？）

**字体与排版：**
（标题字号占比？字体风格是手写还是黑体？重点词有没有变色/加粗？）

**视觉钩子：**
（第一眼最吸睛的元素是什么？是夸张表情、具体数字还是实物特写？）

**氛围感：**
（精致、粗糙真实、焦虑、温馨？）

请用简洁但专业的语言输出，每项不超过50字。"""

# ==================== Full Content Analysis Prompt ====================

FULL_ANALYSIS_PROMPT = """【指令】
你是一位自媒体爆款文案拆解专家，你有七个核心维度的系统化拆解标准：
1. 钩子层（前3秒/首句）
核心逻辑： 关注如何瞬间抓住用户注意力。
分析要点：
	钩子类型： 悬念、冲突、利益承诺、反常识、身份认同。
	情绪反应： 目标人群看到后的即时情绪。
	信息密度： 是否一句话交代了"谁+什么事+为什么要看"。
2. 选题层（内容价值）
核心逻辑： 关注内容的主题价值，决定生死。
分析要点：
	切入点： 痛点、痒点还是爽点？
	时效性： 是蹭热点还是常青话题？
	社交货币： 用户看完是否想转发或收藏？
	竞争度与差异化： 别人写过多少次？这篇有什么不同？
3. 结构层（逻辑骨架）
核心逻辑： 关注文章的组织方式，决定是否易读及完播。
分析要点：
	整体框架： 采用了哪种经典结构？（如：总分总、提出问题-解决方案、讲故事弧线、干货清单体）。
	节奏设计： "留人"技巧，每隔多少内容设置新钩子防止滑走。
	信息颗粒度： 是讲大道理（大而全）还是切入具体点（小而精）。
4. 情绪层（心理共鸣）
核心逻辑： 关注情绪价值，决定互动（点赞/评论/转发）。
分析要点：
	主打情绪： 调动了何种情绪？（焦虑、好奇、愤怒、认同、优越感、获得感）。
	情绪曲线： 开头、中间、结尾的情绪起伏设计。
	情绪共振点： 哪句话或情节最戳中用户，引发评论欲望。
5. 表达层（语言风格）
核心逻辑： 关注文字细节，决定"人设"和阅读体验。
分析要点：
	人设语气： 说话者身份（高高在上的专家、分享的朋友、路人视角）。
	金句密度： 是否有让人眼前一亮、易于摘抄转发的句子。
	口语化程度： 读起来是否顺口，有无生硬的"书面感"障碍词。
6. 视觉/排版层（图文适用）
核心逻辑： 关注第一眼印象和阅读舒适度。
分析要点：
	封面/首图效率： 1秒内传达核心信息，吸引点击。
	排版呼吸感： 段落短小、恰当使用 emoji、加粗/变色标注重点，避免密密麻麻。
	图文配合： 图片是单纯装饰，还是解释文字/增强冲击力。
7. 互动设计层（行为引导）
核心逻辑： 引导用户产生行为。
分析要点：
埋"槽点": 故意留出讨论、吐槽或争论点。
CTA（行动呼吁）： 结尾明确指令（如"点赞再走"、"评论区见"、"收藏防走丢"）。
评论区运营： 作者置顶话术、回复引导深层讨论。

【任务】你需要根据以下内容，完成一篇爆款笔记的拆解。
----------

【第一部分：战略背景（决定爆款含金量）】

所属赛道： {industry}
账号当前粉丝量： {follower_count}
发布时间： {published_at}
数据表现： 点赞 {likes}，收藏 {saves}，评论 {comments}
注意： 请根据粉丝量和数据表现，判断这是否属于"低粉爆款"？如果是，请重点分析它是如何突破粉丝基数限制的。

【第二部分：内容本体】

标题/封面文案：
{title}

正文/脚本全文：
{content}

【第三部分：视觉与互动】

视觉描述：
{visual_description}

高赞评论（用户反馈）：
{top_comments}

----------

【输出要求】

**先下结论：** 这篇内容为什么火？是靠内容质量、靠热点时机、还是靠账号权重？

**7层拆解：** 按照钩子、选题、结构、情绪、表达、视觉、互动进行详细分析。

**模仿建议：** 作为一个博主，我如果想模仿这篇，最应该保留的"灵魂"是什么？最应该修改的"皮肉"是什么？"""


# ==================== Helper Functions ====================

def format_full_analysis_prompt(
    industry: str,
    follower_count: int,
    published_at: str,
    likes: int,
    saves: int,
    comments: int,
    title: str,
    content: str,
    visual_description: str,
    top_comments: str
) -> str:
    """
    Format the full analysis prompt with actual data.

    Args:
        industry: Content category/industry
        follower_count: Account follower count
        published_at: Publication date
        likes: Number of likes
        saves: Number of saves
        comments: Number of comments
        title: Content title
        content: Main content body
        visual_description: Visual description of images
        top_comments: Top user comments

    Returns:
        Formatted prompt string
    """
    return FULL_ANALYSIS_PROMPT.format(
        industry=industry or "未指定",
        follower_count=follower_count,
        published_at=published_at or "未指定",
        likes=likes,
        saves=saves,
        comments=comments,
        title=title,
        content=content,
        visual_description=visual_description or "无",
        top_comments=top_comments or "无"
    )


def format_image_analysis_prompt(image_type: str = "图片") -> str:
    """
    Format the image analysis prompt.

    Args:
        image_type: Type of image (e.g., "封面图", "内容图")

    Returns:
        Formatted prompt string
    """
    return IMAGE_ANALYSIS_PROMPT.format(image_type=image_type)
