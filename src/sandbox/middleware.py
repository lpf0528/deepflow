from typing import NotRequired, override
from src.agent.thread_state import ThreadDataState, SandboxState
from langchain.agents.middleware import AgentMiddleware
from langchain.agents import AgentState
from langgraph.runtime import Runtime

class SandboxMiddlewareState(AgentState):
    """State schema for sandbox middleware."""
    thread_data = NotRequired[ThreadDataState | None]
    sandbox: NotRequired[SandboxState | None]


class SandboxMiddleware(AgentMiddleware[SandboxMiddlewareState]):
    """Sandbox middleware for agent."""
    state_schema = SandboxMiddlewareState

    def __init__(self, lazy_init: bool = True):
        super().__init__()
        self._lazy_init = lazy_init

def _acquire_sandbox(self, thread_id: str):
    pass


@override
def before_agent(self, state: SandboxMiddlewareState, runtime: Runtime) -> dict | None:
    if self._lazy_init:
        return super().before_agent(state, runtime)

    if 'sandbox' not in state or state['sandbox'] is None:
        thread_id = runtime.context['thread_id']
        sandbox_id = self._acquire_sandbox(thread_id)
        return {
            'sandbox': {
                'sandbox_id': sandbox_id
            }
        }
    return super().before_agent(state, runtime)
