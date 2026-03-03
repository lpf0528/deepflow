from langchain.tools import tool, ToolRuntime
from langgraph.typing import ContextT
from src.agent.thread_state import ThreadState
# from

@tool('read_file', parse_docstring=True)
def read_file_tool(
    runtime: ToolRuntime[ContextT, ThreadState]  # 表示该函数可能在某个运行时环境中执行，并且可以访问上下文或线程状态信息。
):
    pass



@tool('ls', parse_docstring=True)
def ls_tool(
    runtime: ToolRuntime[ContextT, ThreadState],  # 表示该函数可能在某个运行时环境中执行，并且可以访问上下文或线程状态信息。
    description: str,
    path: str
) -> str:
    """列出目录内容，深度最多为2级，采用树形格式。

    Args:
        description: 简要说明为什么要列出该目录。务必首先提供此参数。
        path: 要列出的目录路径。
    """
