from pydantic import BaseModel, Field


class TitleConfig(BaseModel):
    """标题配置
    """
    enabled: bool = Field(default=True, description="是否启用标题生成")
    max_words: int = Field(default=10, ge=1, le=20, description="标题最大单词数")
    max_chars: int = Field(default=60, ge=10, le=200, description="标题最大字符数")
    model_name: str | None = Field(default=None, description="标题生成模型名称")
    prompt_template: str = Field(default=('生成简洁对话标题（最多{max_words}词）\n用户：{user_msg}\n助手：{assistant_msg}\n\n仅返回标题，无引号，无解释。'), description="标题生成提示模板")


_title_config: TitleConfig = TitleConfig()


def get_title_config() -> TitleConfig:
    """Get the current title configuration."""
    return _title_config
