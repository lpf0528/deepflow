from typing import NotRequired, override
from langchain.agents.state import AgentState
from langchain.agents.middleware import AgentMiddleware
from langgraph.runtime import Runtime
from src.config.title_config import get_title_config
from src.models.factory import create_chat_model

class TitleMiddlewareState(AgentState):
    title: NotRequired[str | None]

class TitleMiddleware(AgentMiddleware):
    state_schema = TitleMiddlewareState

    def _should_generate_title(self, state: TitleMiddlewareState) -> bool:
        """检查是否需要生成标题
        """
        config = get_title_config()
        if not config.enabled:
            return False

        if state.title:
            return False

        messages = state.get('messages', [])
        if len(messages) < 2:
            return False

        user_messages = [m for m in messages if m.type == 'user']
        assistant_messages = [m for m in messages if m.type == 'ai']
        # 对话初次交流后生成标题
        return len(user_messages) == 1 and len(assistant_messages) >= 1


    def _generate_title(self, state: TitleMiddlewareState) -> str:
        """生成标题
        """
        messages = state.get('messages', [])
        # 从迭代器中获取第一个元素
        user_msg_content = next((m.content for m in messages if m.type == 'user'), '')
        assistant_msg_content = next((m.content for m in messages if m.type == 'ai'), '')

        user_msg = str(user_msg_content) if user_msg_content else ""
        assistant_msg = str(assistant_msg_content) if assistant_msg_content else ""

        config = get_title_config()

        # 获取标题生成模型
        model = create_chat_model(thinking_enabled=False)

        # 构建标题生成提示
        prompt = config.prompt_template.format(
            max_words=config.max_words,
            user_msg=user_msg[:5000],
            assistant_msg=assistant_msg[:5000]
        )

        try:
            # 调用模型生成标题
            response = model.invoke(prompt)
            title_content = str(response.content) if response.content else ""
            title = title_content.strip().strip('"').strip("'")
            return title if len(title) <= config.max_chars else title[:config.max_chars]
        except Exception:
            # 处理异常情况，返回默认标题
            fallback_chars = min(config.max_chars, 50)
            if len(user_msg) > fallback_chars:
                return user_msg[:fallback_chars].strip() + "..."
            return user_msg.strip() if user_msg else "New Conversation"

    @override
    def after_agent(self, state: TitleMiddlewareState, runtime: Runtime) -> dict | None:
        if self._should_generate_title(state):
            title = self._generate_title(state)
            return {
                'title': title
            }
        return None
