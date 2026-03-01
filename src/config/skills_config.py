from pathlib import Path
from pydantic import BaseModel, Field

class SkillsConfig(BaseModel):
    path: str | None = Field(default=None, description="技能目录路径")
    container_path: str = Field(default='/mnt/skills', description="容器内技能目录路径")


    def get_skills_path(self) -> Path:
        """获取技能目录路径
        """
        if self.path:
            path = Path(self.path)
            # 判断路径是否为绝对路径
            if not path.is_absolute():
                path = Path.cwd() / path
            return path.resolve()  # 将路径解析为 绝对路径

        # 默认值：相对于后端目录的 `../skills`
        return Path(__file__).parent.parent.parent / 'skills'
