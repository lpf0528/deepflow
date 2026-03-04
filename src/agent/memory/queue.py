
from datetime import datetime
import time

import threading
from typing import Any
from src.config.memory_config import get_memory_config
from src.agent.memory.updater import MemoryUpdater
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
        # 队列锁，用于保护队列操作的线程安全
        self._lock = threading.Lock()
        # 对话上下文队列，存储待处理的更新
        self._queue: list[ConversationContext] = []
        # 防抖定时器，用于延迟处理队列
        self._timer: threading.Timer | None = None
        # 处理标志，用于防止重复处理
        self._processing: bool = False

    def add(self, thread_id: str, messages: list[Any]) -> None:
        """添加对话到更新队列中
        """

        config = get_memory_config()
        if not config.enabled:
            return

        context = ConversationContext(
            thread_id=thread_id, messages=messages
        )

        # 线程安全：确保在添加时队列不会被其他线程修改
        with self._lock:
            # 去重替换：存在同一个thread_id的上下文，只保留最新的
            self._queue = [c for c in self._queue if c.thread_id != thread_id]
            self._queue.append(context)

            # 重置或开启防抖定时器
            self._reset_timer()


    def _reset_timer(self) -> None:
        """重置或开启防抖定时器
        """
        config = get_memory_config()

        if self._timer is not None:
            self._timer.cancel()

        # 防抖计时器， 到期后批量执行
        self._timer = threading.Timer(
            config.debounce_seconds, self._process_queue
        )
        # 设置为守护线程，确保在主线程退出时自动结束
        self._timer.daemon = True
        self._timer.start()

    def _process_queue(self) -> None:
        """处理所有已排队的对话上下文。
        """

        with self._lock:

            # 防止并发处理
            if self._processing:
                self._reset_timer()
                return
            if not self._queue:
                return

            self._processing = True
            contexts_to_process = self._queue.copy()
            self._queue.clear()
            self._timer = None

        try:
            updater = MemoryUpdater()
            for context in contexts_to_process:
                try:
                    success = updater.update_memory(
                        messages=context.messages,
                        thread_id=context.thread_id,
                    )
                    if success:
                        print(f"Successfully updated memory for thread {context.thread_id}")
                    else:
                        print(f"Failed to update memory for thread {context.thread_id}")
                except Exception as e:
                    print(f"Error updating memory for thread {context.thread_id}: {e}")

                # 在更新之间设置小延迟以避免速率限制
                if len(contexts_to_process) > 1:
                    time.sleep(0.5)
        finally:
            self._processing = False

    @property
    def pending_count(self) -> int:
        """Get the number of pending updates."""
        with self._lock:
            return len(self._queue)


_memory_queue: MemoryUpdateQueue | None = None
_queue_lock = threading.Lock()

def get_memory_queue() -> MemoryUpdateQueue:
    global _memory_queue
    with _queue_lock:
        if _memory_queue is None:
            _memory_queue = MemoryUpdateQueue()
    return _memory_queue
