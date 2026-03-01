from abc import ABC, abstractmethod
from src.sandbox.sandbox import Sandbox

class SandboxProvider(ABC):
    @abstractmethod
    def acquire(self, thread_id: str | None = None) -> str:
        """获取一个沙箱环境并返回其ID
        """
        pass

    @abstractmethod
    def get(self, sandbox_id: str) -> Sandbox | None:
        """根据沙箱ID获取沙箱环境
        """
        pass

    @abstractmethod
    def release(self, sandbox_id: str) -> None:
        """释放沙箱环境
        """
        pass


_default_sandbox_provider: SandboxProvider | None = None

def get_sandbox_provider(**kwargs) -> SandboxProvider:
    global _default_sandbox_provider
    if _default_sandbox_provider is None:

        _default_sandbox_provider = SandboxProvider(**kwargs)

    return _default_sandbox_provider
