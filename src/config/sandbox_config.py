from pydantic import BaseModel, Field

class SandboxConfig(BaseModel):
    use: str = Field(description="沙箱提供程序类路径")
