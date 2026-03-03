import os
import yaml
from pydantic import BaseModel, Field
from typing import Self, Any
from pathlib import Path
from src.config.sandbox_config import SandboxConfig
from src.config.skills_config import SkillsConfig
from src.config.model_config import ModelConfig

class AppConfig(BaseModel):
    sandbox: SandboxConfig = Field(description="沙箱配置")
    models: list[ModelConfig] = Field(description="模型配置")
    skills: SkillsConfig = Field(default_factory=SkillsConfig, description="技能配置")

    @classmethod
    def resolve_config_path(cls, config_path: str | None = None) -> Path:
        """解析配置文件路径
        """
        if config_path:
            path = Path(config_path)
            if path.exists():
                raise FileNotFoundError(f"配置文件路径不存在: {config_path}")
            return path
        else:
            # 获取当前工作目录
            path = Path(os.getcwd()) / 'config.yaml'
            if not path.exists():
                raise FileNotFoundError(f"配置文件路径不存在: {path}")
            return path

    @classmethod
    def resolve_env_variables(cls, config: Any) -> Any:
        """递归解析配置中的环境变量
        环境变量通过 os.getenv 函数进行解析。例如：$OPENAI_API_KEY
        """
        if isinstance(config, str):
            if config.startswith('$'):
                env_value = os.getenv(config[1:])
                if env_value is None:
                    raise ValueError(f"环境变量 {config} 未设置")
                return env_value
            return config
        elif isinstance(config, dict):
            return {k: cls.resolve_env_variables(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [cls.resolve_env_variables(v) for v in config]
        return config

    @classmethod
    def from_file(cls, config_path: str | None = None) -> Self:
        """从YML文件中加载配置
        """
        resolve_path = cls.resolve_config_path(config_path)
        with open(resolve_path) as f:
            config_data = yaml.safe_load(f)

        config_data = cls.resolve_env_variables(config_data)

        return cls.model_validate(config_data)

    def get_model_config(self, name: str) -> ModelConfig | None:
        """根据模型名称获取模型配置
        """
        return next((model for model in self.models if model.name == name), None)



_app_config: AppConfig = None

def get_app_config() -> AppConfig:
    global _app_config
    if _app_config is None:
        _app_config = AppConfig.from_file()
    return _app_config
