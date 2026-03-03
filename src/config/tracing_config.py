import os
import threading

from pydantic import BaseModel, Field


class TracingConfig(BaseModel):
    """Tracing configuration."""
    # ..表示这个字段是必须的
    enabled: bool = Field(..., description="是否启用跟踪")
    api_key: str = Field(..., description="API密钥")
    project: str = Field(..., description="项目名称")
    endpoint: str = Field(..., description="API端点")

    @property
    def is_configured(self) -> bool:
        """Check if tracing is fully configured (enabled and has API key)."""
        return self.enabled and bool(self.api_key)


_config_lock = threading.Lock()
_tracing_config: TracingConfig | None = None

def get_tracing_config() -> TracingConfig:
    """Get the current tracing configuration."""
    global _tracing_config
    if _tracing_config is not None:
        return _tracing_config

    with _config_lock:
        if _tracing_config is not None:
            return _tracing_config
        _tracing_config = TracingConfig(
            enabled=os.getenv("LANGSMITH_TRACING", "false").lower() == "true",
            api_key=os.getenv("LANGSMITH_API_KEY", ""),
            project=os.getenv("LANGSMITH_PROJECT", "default"),
            endpoint=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"),
        )
    return _tracing_config



def is_tracing_enabled() -> bool:
    """Check if tracing is enabled."""
    return get_tracing_config().is_configured
