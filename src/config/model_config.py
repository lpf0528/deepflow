from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    name: str = Field(description="模型名称")
    use: str = Field(description="模型实现类")
    model: str = Field(description="模型ID")
    api_key: str = Field(description="API密钥")
    temperature: float = Field(description="温度")
    max_tokens: int = Field(description="最大令牌数")
