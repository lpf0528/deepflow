from typing import NotRequired
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from langgraph.runtime import Runtime
from src.agent.thread_state import ThreadDataState
from src.config.paths import get_paths
from typing import override

class ThreadDataMiddlewareState(AgentState):
    thread_data = NotRequired[ThreadDataState | None]

class ThreadDataMiddleware(AgentMiddleware[ThreadDataMiddlewareState]):
    """为每个线程执行创建线程数据目录。

    创建以下目录结构：
    - {base_dir}/threads/{thread_id}/user-data/workspace
    - {base_dir}/threads/{thread_id}/user-data/uploads
    - {base_dir}/threads/{thread_id}/user-data/outputs

    生命周期管理：
    - 当lazy_init=True（默认）时：仅计算路径，目录按需创建
    - 当lazy_init=False时：在before_agent()阶段立即创建目录
    """
    state_schema = ThreadDataMiddlewareState

    def __init__(self, base_dir: str | None = None, lazy_init: bool = True):
        self._path = get_paths()

    def _get_thread_paths(self, thread_id: str) -> dict[str, str]:
        return {
            'workspace_path': self._path.sandbox_work_dir(thread_id),
            'uploads_path': self._path.sandbox_uploads_dir(thread_id),
            'outputs_path': self._path.sandbox_outputs_dir(thread_id),
        }

    def _create_thread_directories(self, thread_id: str) -> dict[str, str]:
        self._path.ensure_thread_dirs(thread_id)
        return self._get_thread_paths(thread_id)



    @override
    def before_agent(self, state: ThreadDataMiddlewareState, runtime: Runtime):
        thread_id = runtime.context.get('thread_id')
        paths = self._create_thread_directories(thread_id)
        return {
            "thread_data": {
                **paths
            }
        }
