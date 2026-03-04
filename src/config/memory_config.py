
from pydantic import BaseModel, Field

class MemoryConfig(BaseModel):
    enabled: bool = Field(default=True, description="是否启用内存")
    storage_path: str = Field(default="", description=(
        "用于存储记忆数据的路径。"
        "如果留空，默认为 `{base_dir}/memory.json`（参见 Paths.memory_file）。"
        "绝对路径会按原样使用。"
        "相对路径将相对于 `Paths.base_dir` 进行解析（而非后台工作目录）。"
        "注意：如果你之前将其设置为 `.deer-flow/memory.json`，"
        "那么现在文件将解析为 `{base_dir}/.deer-flow/memory.json`；"
        "请迁移现有数据或使用绝对路径以保持旧位置。"
    ))
    debounce_seconds: int = Field(default=10, ge=1, le=300, description='处理排队更新之前等待的毫秒数（去抖动）。')
    model_name : str | None = Field(default=None, description='用于记忆的模型名称。')
    max_facts: int = Field(default=100, ge=10, le=500, description='要存储的事实的最大数量。')
    fact_confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description='存储事实的最低置信度阈值')
    max_injection_tokens: int = Field(default=2000, ge=100, le=8000, description='每次注入记忆的最大令牌数')



_memory_config: MemoryConfig() = MemoryConfig()


def get_memory_config() -> MemoryConfig:
    return _memory_config


def set_memory_config(config: MemoryConfig) -> None:
    global _memory_config
    _memory_config = config

def load_memory_config_from_dict(config_dict: dict) -> None:
    set_memory_config(MemoryConfig(**config_dict))
