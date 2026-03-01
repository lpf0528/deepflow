from langchain.tools import tool, ToolRuntime
from langgraph.typing import ContextT
from src.agent.thread_state import ThreadState
# from

@tool('read_file', parse_docstring=True)
def read_file_tool(
    runtime: ToolRuntime[ContextT, ThreadState]  # 表示该函数可能在某个运行时环境中执行，并且可以访问上下文或线程状态信息。
):
    pass
