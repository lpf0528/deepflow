from typing import Any


MEMORY_UPDATE_PROMPT = """你是一个记忆管理系统。你的任务是分析对话并更新用户的记忆档案。

当前记忆状态:
<当前记忆>
{current_memory}
</当前记忆>

待处理的新对话:
<对话>
{conversation}
</对话>

操作说明:
1. 分析对话，提取关于用户的重要信息
2. 提取相关事实、偏好和背景(包含具体数字、人名、技术名称)
3. 按照以下详细的长度规范更新各记忆模块

**记忆模块规范**

**用户上下文**(当前状态——简明摘要):
- workContext(工作背景):职业角色、所在公司、核心项目、主要技术栈(2~3句话)
  示例:核心贡献者、含指标的项目名称(如16k+ stars)、技术栈
- personalContext(个人背景):语言能力、沟通偏好、主要兴趣(1~2句话)
  示例:双语能力、具体兴趣领域、专长方向
- topOfMind(当前关注):多个正在进行的关注点与优先事项(3~5句话，详细段落)
  示例:主要项目进展、并行技术探索、持续学习与跟踪的内容
  包含:活跃的实施工作、待解决问题、市场/研究兴趣
  注意:此项需捕捉多个并发关注点，而非单一任务

**历史记录**(时间维度——详细段落):
- recentMonths(近期动态):近期活动的详细摘要(4~6句话或1~2段)
  时间范围:近1~3个月的互动
  包含:探索的技术、参与的项目、解决的问题、展现的兴趣
- earlierContext(较早背景):仍具参考价值的历史规律(3~5句话或1段)
  时间范围:3~12个月前
  包含:过往项目、学习历程、已建立的行为模式
- longTermBackground(长期背景):持久性的基础背景信息(2~4句话)
  时间范围:整体/基础信息
  包含:核心专长、长期兴趣、基本工作风格

**事实提取规范**:
- 提取具体、可量化的细节(如"GitHub 16k+ stars"、"200+数据集")
- 包含专有名词(公司名、项目名、技术名称)
- 保留技术术语及版本号
- 分类说明:
  * preference(偏好):用户倾向或不喜欢的工具、风格、方式
  * knowledge(知识):掌握的具体技术、专业领域知识
  * context(背景):基础事实(职位、项目、地点、语言)
  * behavior(行为):工作习惯、沟通方式、解决问题的模式
  * goal(目标):明确表达的目标、学习计划、项目愿景
- 置信度说明:
  * 0.9~1.0:明确陈述的事实("我在做X"、"我的职位是Y")
  * 0.7~0.8:从行为/讨论中强烈推断
  * 0.5~0.6:推断出的规律(谨慎使用，仅适用于明显规律)

**各模块内容归属说明**:
- workContext:当前工作、活跃项目、主要技术栈
- personalContext:语言能力、性格特点、工作之外的兴趣
- topOfMind:用户近期关注的多个并发优先事项(更新最频繁)
  应涵盖3~5个并发主题:主线工作、旁线探索、学习/跟踪兴趣
- recentMonths:近期技术探索与工作的详细记录
- earlierContext:仍具参考价值的稍早互动规律
- longTermBackground:关于用户的不变基础事实

**多语言内容处理**:
- 专有名词和公司名保留原始语言
- 技术术语保持原始形式(如DeepSeek、LangGraph等)
- 在personalContext中注明语言能力

输出格式(JSON):
```json
{
  "user": {
    "workContext": { "summary": "...", "shouldUpdate": true/false },
    "personalContext": { "summary": "...", "shouldUpdate": true/false },
    "topOfMind": { "summary": "...", "shouldUpdate": true/false }
  },
  "history": {
    "recentMonths": { "summary": "...", "shouldUpdate": true/false },
    "earlierContext": { "summary": "...", "shouldUpdate": true/false },
    "longTermBackground": { "summary": "...", "shouldUpdate": true/false }
  },
  "newFacts": [
    { "content": "...", "category": "preference|knowledge|context|behavior|goal", "confidence": 0.0-1.0 }
  ],
  "factsToRemove": ["fact_id_1", "fact_id_2"]
}
```

**重要规则**:
- 仅当存在有意义的新信息时，才将 shouldUpdate 设为 true
- 遵守长度规范:workContext/personalContext 简洁(1~3句)，topOfMind 及历史模块详细(段落形式)
- 事实中须包含具体指标、版本号和专有名词
- 仅添加明确陈述(0.9+)或强烈推断(0.7+)的事实
- 删除与新信息相矛盾的旧事实
- 更新 topOfMind 时，整合新关注点，同时移除已完成或已放弃的内容，保留3~5个仍活跃的并发主题
- 历史模块更新时，按时间顺序将新信息整合至对应时段
- 保持技术准确性——技术名称、公司名、项目名须完整保留
- 聚焦于对未来交互和个性化有价值的信息

**仅返回合法的 JSON，不附带任何解释或 Markdown 格式。**

"""

def format_conversation_for_update(messages: list[Any]) -> str:
    """格式化对话为更新文本
    """
    lines = []
    for msg in messages:
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", str(msg))

        # Handle content that might be a list (multimodal)
        if isinstance(content, list):
            text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and "text" in p]
            content = " ".join(text_parts) if text_parts else str(content)

        # Truncate very long messages
        if len(str(content)) > 1000:
            content = str(content)[:1000] + "..."

        if role == "human":
            lines.append(f"User: {content}")
        elif role == "ai":
            lines.append(f"Assistant: {content}")

    return "\n\n".join(lines)
