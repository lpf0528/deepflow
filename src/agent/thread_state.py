from typing import NotRequired, Annotated, TypedDict
from langchain.agents import AgentState

class SandboxState(TypedDict):
    """State schema for sandbox middleware."""
    sandbox_id: NotRequired[str | None]

class ThreadDataState(TypedDict):
    workspace_path: NotRequired[str | None]
    uploads_path: NotRequired[str | None]
    outputs_path: NotRequired[str | None]


class ThreadState(AgentState):
    # sandbox: NotRequired[SandboxState | None]
    # thread_data: NotRequired[ThreadDataState | None]
    title: NotRequired[str | None]
    # artifacts（产物）指agent在沙箱中写入的文件（如代码、报告、网页）
    # artifacts: Annotated[list[str], merge_artifacts]
    todos: NotRequired[list | None]
    uploaded_files: NotRequired[list[dict] | None]
    # viewed_images: Annotated[dict[str, ViewedImageDate], merge_viewed_images]
