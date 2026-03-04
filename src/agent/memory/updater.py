import json
import uuid

from datetime import datetime

from pathlib import Path
import time
from typing import Any
from src.config.memory_config import get_memory_config
from src.config.paths import get_paths
from src.agent.memory.prompt import format_conversation_for_update, MEMORY_UPDATE_PROMPT
from src.models.factory import create_chat_model
# 全局的记忆数据缓存
_memory_data: dict[str, Any] | None = None
# 跟踪文件修改时间以实现缓存失效
_memory_file_mtime: float | None = None

class MemoryUpdater:


    def update_memory(self, messages: list[Any], thread_id: str) -> bool:
        """更新用户记忆
        """
        config = get_memory_config()
        if not config.enabled:
            return False

        if not messages:
            return False

        # 获取当前的记忆
        current_memory = get_memory_data()
        conversation_text = format_conversation_for_update(messages)
        if not conversation_text.strip():
            return False

        # 构建提示词
        prompt = MEMORY_UPDATE_PROMPT.format(
            conversation=conversation_text,
            current_memory=json.dumps(current_memory, ensure_ascii=False, indent=2)
        )

        model = self._get_mode()
        response = model.invoke(prompt)
        response_text = str(response.content).strip()

        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        update_data = json.loads(response_text)
        updated_memory = self._apply_updates(current_memory, update_data, thread_id)

        return _save_memory_to_file(updated_memory)

    def _apply_updates(self, current_memory: dict[str, Any], update_data: dict[str, Any], thread_id: str | None = None) -> dict[str, Any]:
        """应用更新数据到当前记忆
        """
        config = get_memory_config()
        now = datetime.utcnow().isoformat() + 'Z'

        # 更新user记忆
        user_updates = update_data.get('user', {})
        for section in ['workContext', 'personalContext', 'topOfMind']:
            section_data = user_updates.get(section, {})
            if section_data.get('shouldUpdate') and section_data.get('summary'):
                current_memory['user'][section] = {
                    'summary': section_data['summary'],
                    'updatedAt': now
                }

        history_updates = update_data.get("history", {})
        for section in ["recentMonths", "earlierContext", "longTermBackground"]:
            section_data = history_updates.get(section, {})
            if section_data.get("shouldUpdate") and section_data.get("summary"):
                current_memory["history"][section] = {
                    "summary": section_data["summary"],
                    "updatedAt": now,
                }
        facts_to_remove = set(update_data.get("factsToRemove", []))
        if facts_to_remove:
            current_memory["facts"] = [f for f in current_memory.get("facts", []) if f.get("id") not in facts_to_remove]

        # Add new facts
        new_facts = update_data.get("newFacts", [])
        for fact in new_facts:
            confidence = fact.get("confidence", 0.5)
            if confidence >= config.fact_confidence_threshold:
                fact_entry = {
                    "id": f"fact_{uuid.uuid4().hex[:8]}",
                    "content": fact.get("content", ""),
                    "category": fact.get("category", "context"),
                    "confidence": confidence,
                    "createdAt": now,
                    "source": thread_id or "unknown",
                }
                current_memory["facts"].append(fact_entry)

        # Enforce max facts limit
        if len(current_memory["facts"]) > config.max_facts:
            # Sort by confidence and keep top ones
            current_memory["facts"] = sorted(
                current_memory["facts"],
                key=lambda f: f.get("confidence", 0),
                reverse=True,
            )[: config.max_facts]

        return current_memory


    def _get_mode(self) -> str:
        """获取更新模式
        """
        config = get_memory_config()
        model_name = self._model_name or config.model_name
        return create_chat_model(name=model_name, thinking_enabled=False)


def _save_memory_to_file(memory_data: dict[str, Any]) -> bool:
    global _memory_data, _memory_file_mtime
    file_path = _get_memory_file_path()

    try:

        file_path.parent.mkdir(parents=True, exist_ok=True)

        memory_data["lastUpdated"] = datetime.utcnow().isoformat() + "Z"

        temp_path = file_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, indent=2, ensure_ascii=False)

        temp_path.replace(file_path)

        _memory_data = memory_data
        try:
            _memory_file_mtime = file_path.stat().st_mtime
        except OSError:
            _memory_file_mtime = None

        print(f"Memory saved to {file_path}")
        return True
    except OSError as e:
        print(f"Failed to save memory file: {e}")
        return False

def get_memory_data() -> dict[str, Any]:
    """获取用户记忆数据
    """
    global _memory_data, _memory_file_mtime

    file_path = _get_memory_file_path()

    try:
        # 获取文件修改时间
        current_mtime = file_path.stat().st_mtime if file_path.exists() else None
    except OSError:
        current_mtime = None

    if _memory_data is None or _memory_file_mtime != current_mtime:
        # 缓存未初始化或文件已修改，需要重新加载
        _memory_data = _load_memory_file()
        _memory_file_mtime = current_mtime
    return _memory_data

def _create_empty_memory() -> dict[str, Any]:
    return {
        "version": "1.0",
        'lastUpdated': datetime.utcnow().isoformat() + 'Z',
        'user': {
            # 工作记忆
            'workContext': {'summary': '', 'updatedAt': ''},
            # 个人记忆
            'personalContext': {'summary': '', 'updatedAt': ''},
            # 核心记忆
            'topOfMind': {'summary': '', 'updatedAt': ''}
        },
        'history': {
            # 最近月份记忆
            "recentMonths": {"summary": "", "updatedAt": ""},
            # 更早记忆
            "earlierContext": {"summary": "", "updatedAt": ""},
            # 长期背景记忆
            "longTermBackground": {"summary": "", "updatedAt": ""},
        },
        'facts': []
    }

def _load_memory_file() -> dict[str, Any]:
    file_path = _get_memory_file_path()

    if not file_path.exists():
        return _create_empty_memory()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return _create_empty_memory()



def _get_memory_file_path() -> Path:
    """获取记忆文件路径
    """
    config = get_memory_config()
    if config.storage_path:
        p = Path(config.storage_path)
        return p if p.is_absolute() else get_paths().base_dir / p
    return get_paths().memory_file
