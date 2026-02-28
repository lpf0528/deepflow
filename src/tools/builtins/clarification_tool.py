from langchain.tools import tool
from typing import Literal


@tool('ask_clarification', parse_docstring=True, return_direct=True)
def ask_clarification_tool(
    question: str,
    clarification_type: Literal[
        "missing_info",
        "ambiguous_requirement",
        "approach_choice",
        "risk_confirmation",
        "suggestion"
    ],
    content: str | None = None,
    options: list[str] | None = None
):
    """
    当你需要更多信息才能继续时，向用户寻求澄清。

    在以下情况下使用此工具，即没有用户输入就无法继续时：

    - **信息缺失**：未提供必要的详细信息（例如文件路径、URL、具体需求）
    - **需求模糊**：存在多种有效解释
    - **方案选择**：存在多种有效方案，需要用户偏好
    - **风险操作**：需要明确确认的破坏性操作（例如删除文件、修改生产环境）
    - **建议确认**：你有推荐方案，但希望在继续之前获得用户批准

    执行将被中断，问题将呈现给用户。等待用户响应后再继续。

    何时使用 ask_clarification：
    - 你需要用户请求中未提供的信息
    - 需求可以有多种解释方式
    - 存在多种有效的实现方案
    - 你即将执行潜在危险的操作
    - 你有推荐方案但需要用户批准

    最佳实践：
    - 每次只问**一个**澄清问题，以保持清晰
    - 问题要具体明确
    - 需要澄清时不要做假设
    - 对于风险操作，**务必**要求确认
    - 调用此工具后，执行将自动中断

    Args:
    - `question`：向用户提出的澄清问题，需具体明确。
    - `clarification_type`：所需澄清的类型（missing_info 缺失信息、ambiguous_requirement 需求模糊、approach_choice 方案选择、risk_confirmation 风险确认、suggestion 建议确认）。
    - `context`：可选，说明为何需要澄清的上下文，帮助用户理解情况。
    - `options`：可选，选项列表（适用于 approach_choice 或 suggestion 类型），为用户呈现清晰的选择。
    """
    # 这是一个占位符实现
    # 实际逻辑由 ClarificationMiddleware 处理，它会拦截此工具调用
    # 并中断执行，将问题呈现给用户
    return "Clarification request processed by middleware"
