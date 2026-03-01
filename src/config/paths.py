
import re
from pathlib import Path
_SAFE_THREAD_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")

class Paths:


    def __init__(self, base_dir: str | Path | None = None):
        self._base_dir = Path(base_dir).resolve() if base_dir else None

    @property
    def base_dir(self) -> Path:
        if self._base_dir:
            return self._base_dir

        # 当前工作目录的路径
        cwd = Path.cwd()
        if cwd.name == 'backend' or (cwd / "pyproject.toml").exists():
            return cwd / ".deer-flow"
        # 当前用户的主目录路径
        return Path.home() / ".deer-flow"

    def ensure_thread_dirs(self, thread_id: str):
        self.sandbox_work_dir(thread_id).mkdir(parents=True, exist_ok=True)
        self.sandbox_uploads_dir(thread_id).mkdir(parents=True, exist_ok=True)
        self.sandbox_outputs_dir(thread_id).mkdir(parents=True, exist_ok=True)

    def sandbox_work_dir(self, thread_id: str) -> Path:
        """
        Host path for the agent's workspace directory.
        Host: `{base_dir}/threads/{thread_id}/user-data/workspace/`
        Sandbox: `/mnt/user-data/workspace/`
        """
        return self.thread_dir(thread_id) / 'user-data' / "workspace"

    def sandbox_uploads_dir(self, thread_id: str) -> Path:
        return self.thread_dir(thread_id) / 'user-data' / "uploads"

    def sandbox_outputs_dir(self, thread_id: str) -> Path:
        return self.thread_dir(thread_id) / 'user-data' / "outputs"

    def thread_dir(self, thread_id: str) -> Path:

        if not _SAFE_THREAD_ID_RE.match(thread_id):
            raise ValueError(f"Invalid thread_id: {thread_id}")

        return self.base_dir / 'threads' / thread_id


_paths: Paths | None = None

def get_path() -> Paths:
    global _paths
    if _paths is None:
        _paths = Paths()
    return _paths


if __name__ == '__main__':
    print(get_path().base_dir)
