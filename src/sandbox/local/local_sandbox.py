from src.sandbox.local.sandbox import Sandbox


class LocalSandbox(Sandbox):
    def __init__(self, id: str, path_mappings: dict[str, str] | None = None):
        super().__init__(id)
        self.path_mappings = path_mappings or {}


    def _resolve_path_in_command(self, command: str) -> str:
        """解析命令中的路径映射。
        """
        for key, value in self.path_mappings.items():
            command = command.replace(key, value)
        return command


    def execute_command(self, command: str) -> str:
        """在沙盒中执行bash命令
        """


        pass

    def read_file(self, path: str) -> str:
        """读取文件内容。
        """
        pass

    def list_dir(self, path: str, max_depth=2) -> list[str]:
        """列出目录的内容。
        """
        pass

    def write_file(self, path: str, content: str, append: bool = False) -> None:
        """写入文件内容。
        """
        pass

    def update_file(self, path: str, content: bytes) -> None:
        """更新文件内容。
        """
        pass
