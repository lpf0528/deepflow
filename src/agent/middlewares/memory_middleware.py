from typing import override, Any
from langchain.agents.middleware import AgentMiddleware
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from src.config.memory_config import get_memory_config
from src.agent.memory.queue import get_memory_queue

class MemoryMiddlewareState(AgentState):
    pass

class MemoryMiddleware(AgentMiddleware[MemoryMiddlewareState]):
    """中间件用于在代理执行后排队对话以更新记忆。

    这个中间件：
    1. 在每次代理执行后，将对话排队等待记忆更新
    2. 仅包含用户输入和最终的助手回复（忽略工具调用）
    3. 队列使用去抖动技术将多个更新合并在一起
    4. 通过LLM总结异步更新记忆
    """

    state_schema = MemoryMiddlewareState

    def _filter_messages_for_memory(self, messages: list[Any]) -> list[Any]:
        filtered = []
        for msg in messages:
            msg_type = getattr(msg, 'type', None)
            if msg_type == 'human':
                filtered.append(msg)
            elif msg_type == 'ai' and not getattr(msg, 'tool_calls', None):
                filtered.append(msg)
            # 跳过工具消息和AI带有工具调用的消息
        return filtered

    @override
    def after_agent(self, state: MemoryMiddlewareState, runtime: Runtime) -> dict | None:
        config = get_memory_config()
        if not config.enabled:
            return None

        thread_id = runtime.context.get('thread_id')
        if not thread_id:
            return None

        messages = state.get('messages', [])
        if not messages:
            return None

        # 过滤：仅保留用户输入和助手的最终回复。
        filtered_message = self._filter_messages_for_memory(messages)

        user_messages = [msg for msg in filtered_message if getattr(msg, 'type', None) == 'human']
        ai_messages = [msg for msg in filtered_message if getattr(msg, 'type', None) == 'ai']

        if not user_messages or not ai_messages:
            return None

        queue = get_memory_queue()
        queue.add(thread_id, messages=filtered_message)
        return None
