from langchain.agents.middleware import AgentMiddleware
from langchain.agents import AgentState
from typing import override
from langgraph.prebuilt.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from collections.abc import Callable
from langgraph.types import Command
from langgraph.graph import END

class ClarificationMiddlewareState(AgentState):
    """Compatible with the `ThreadState` schema."""
    pass


class ClarificationMiddleware(AgentMiddleware[ClarificationMiddlewareState]):
    """拦截澄清工具调用并中断执行以向用户提出问题。
    当模型调用 `ask_clarification` 工具时，该中间件会：

    1. 在执行前拦截工具调用。
    2. 提取澄清问题和元数据。
    3. 格式化为用户友好的消息。
    4. 返回一个中断执行并呈现问题的命令。
    5. 等待用户响应后再继续。

    这取代了基于工具的方法，其中澄清是继续对话的一部分。
    """
    state_schema = ClarificationMiddlewareState

    @override
    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command]
    ) -> ToolMessage | Command:
        if request.tool_call.get("name") != "ask_clarification":
            # Not a clarification call, execute normally
            return handler(request)
        return self._handle_clarification(request)

    @override
    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command]
    ) -> ToolMessage | Command:
        """Intercept ask_clarification tool calls and interrupt execution (sync version).

        Args:
            request: Tool call request
            handler: Original tool execution handler

        Returns:
            Command that interrupts execution with the formatted clarification message
        """
        if request.tool_call.get("name") != "ask_clarification":
            # Not a clarification call, execute normally
            print(f"Not a clarification call: {request.tool_call}")
            return handler(request)
        print(f"Clarification call: {request.tool_call}")
        return self._handle_clarification(request)


    def _handle_clarification(self, request: ToolCallRequest) -> Command:
        args = request.tool_call.get('args', {})

        formatted_message = self._format_clarification_message(args)

        tool_call_id = request.tool_call.get('id', '')
        tool_message = ToolMessage(
            content=formatted_message,
            name="ask_clarification",
            tool_call_id=tool_call_id
        )
        return Command(
            update={'messages': [tool_message]},
            goto=END
        )


    def _format_clarification_message(self, args: dict) -> str:
        question = args.get('question', '')
        clarification_type = args.get('clarification_type', 'missing_info')
        context = args.get('context', None)
        options = args.get('options', [])


        type_icons = {
            "missing_info": "❓",
            "ambiguous_requirement": "🤔",
            "approach_choice": "🔀",
            "risk_confirmation": "⚠️",
            "suggestion": "💡",
        }
        message_parts = []

        icon = type_icons.get(clarification_type, '❓')
        if context:
            message_parts.extend([f"{icon} {context}", f'\n{question}'])
        else:
            message_parts.append(f"{icon} {question}")

        if options and len(options) > 0:
            message_parts.append('')  # 空行用于间隔。
            message_parts.extend([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        return '\n'.join(message_parts)
