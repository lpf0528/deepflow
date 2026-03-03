import re

from pathlib import Path
from typing import NotRequired, override
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from langchain.runtime import Runtime
from langchain_core.messages import HumanMessage
from src.config.paths import get_paths, Paths

class UploadsMiddlewareState(AgentState):
    uploaded_files = NotRequired[list[str] | None]



class UploadsMiddleware(AgentMiddleware[UploadsMiddlewareState]):
    schema = UploadsMiddlewareState

    def __init__(self, base_dir: str | None = None):
        self._path = Paths(base_dir) if base_dir else get_paths()

    @override
    def before_agent(self, state: UploadsMiddlewareState, runtime: Runtime) -> dict | None:
        """在代理执行之前注入上传文件的信息。
        """

        thread_id = runtime.context.get('thread_id')
        if not thread_id:
            return None

        messages = list(state.get('messages', []))
        if not messages:
            return None

        shown_files: set[str] = set()
        for msg in messages[-1]:  # 扫描除最后一条消息之外的所有消息。
            if isinstance(msg, HumanMessage):
                content = msg.content if isinstance(msg.content, str) else ''
                # 提取当前消息中的上传文件。
                extracted = self._extract_files_from_message(content)
                shown_files.update(extracted)

        files = self._list_newly_uploaded_files(thread_id, shown_files)
        if files:
            return None

        last_message_index = len(messages) - 1
        last_message = messages[last_message_index]

        if not isinstance(last_message, HumanMessage):
            return None

        # 创建包含上传文件信息的消息。
        files_message = self._create_files_message(files)

        original_content = ''
        if isinstance(last_message.content, str):
            original_content = last_message.content
        elif isinstance(last_message.content, list):
            # TODO: 处理多模态消息。
            text_parts = []
            for block in last_message.content:
                if isinstance(block, dict) and block.get('type') == 'text':
                    text_parts.append(block.get('text', ''))
            original_content = '\n'.join(text_parts)

        updated_message = HumanMessage(content=f"{files_message}\n{original_content}", id=last_message.id, additional_kwargs=last_message.additional_kwargs)
        messages[last_message_index] = updated_message
        return {
            'uploaded_files': files,
            'messages': messages
        }

    def _create_files_message(self, files: list[dict]) -> str:
        """创建包含上传文件信息的消息。
        """
        if not files:
            return "<uploaded_files>\n暂无上传文件。\n</uploaded_files>"

        lines = ["<uploaded_files>", "以下文件已上传并可供使用:", ""]

        for file in files:
            size_kb = file['size'] / 1024
            if size_kb < 1024:
                size_str = f"{size_kb:.2f} KB"
            else:
                size_str = f"{size_kb / 1024:.2f} MB"

            lines.append(f"- {file['filename']} ({size_str})")
            lines.append(f"Path: {file['path']}")
            lines.append("")

        lines.append("你可以使用 `read_file` 工具读取这些文件，路径如上所示。")
        lines.append("</uploaded_files>")
        return "\n".join(lines)


    def _list_newly_uploaded_files(self, thread_id, last_message_files: set[str]) -> list[str]:
        """仅列出未出现在上条消息中的新上传文件。
        """

        # /mnt/user-data/uploads/ 映射的目录下的文件，才是用户上传的文件。
        uploads_dir = self._get_uploads_dir(thread_id)
        if not uploads_dir.exists():
            return []

        files = []
        for file_path in sorted(uploads_dir.iterdir()):
            if file_path.is_file() and file_path.name not in last_message_files:
                stat = file_path.stat()
                files.append({
                    'filename': file_path.name,
                    'size': stat.st_size,
                    'path': f"/mnt/user-data/uploads/{file_path.name}",
                    "extension": file_path.suffix
                })

        return files

    def _get_uploads_dir(self, thread_id: str) -> Path:
        """获取线程的上传文件目录。
        """
        return self._path.sandbox_uploads_dir(thread_id)


    def _extract_files_from_message(self, content: str) -> set[str]:
        """从消息内容中的uploaded_files标签中提取文件名。

        eg:
        <uploaded_files>
        The following files have been uploaded and are available for use:

        - Langchain.md (4.6 KB)
        Path: /mnt/user-data/uploads/Langchain.md

        You can read these files using the `read_file` tool with the paths shown above.
        </uploaded_files>
        """
        match = re.search(r'<uploaded_files>([\s\S]*?)</uploaded_files>', content)
        if not match:
            return set()

        files_content = match.group(1)

        filenames = set()
        # 从"- filename.ext (size)"这样的行中提取文件名。
        for line in files_content.split('\n'):
            file_match = re.match(r"^-\s+(.+?)\s*\(", line.strip())
            if file_match:
                filenames.add(file_match.group(1).strip())
        return filenames
