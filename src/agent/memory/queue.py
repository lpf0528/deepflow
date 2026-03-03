
from datetime import datetime
import threading
from typing import Any
from src.config.memory_config import get_memory_config
from dataclasses import dataclass, field

@dataclass
class ConversationContext:
    """用户记忆更新的对话上下文
    """
    thread_id: str
    messages: list[Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class MemoryUpdateQueue:

    def __init__(self):
        self._lock = threading.Lock()
        self._queue: list[ConversationContext] = []

    def add(self, thread_id: str, messages: list[Any]) -> None:
        """添加对话到更新队列中
        """
        config = get_memory_config()
        if not config.enabled:
            return

        context = ConversationContext(
            thread_id=thread_id, messages=messages
        )

        # with self._lock:
        #     self._queue =




_memory_queue: MemoryUpdateQueue | None = None
_queue_lock = threading.Lock()

def get_memory_queue() -> MemoryUpdateQueue:
    global _memory_queue
    with _queue_lock:
        if _memory_queue is None:
            _memory_queue = MemoryUpdateQueue()
    return _memory_queue
