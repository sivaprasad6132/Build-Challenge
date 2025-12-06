from collections import deque
from threading import Lock, Condition


class BoundedBlockingQueue:
    """
    Thread-safe bounded blocking queue implementation.

    Uses:
      - A Lock for mutual exclusion
      - Two Condition variables for wait/notify:
            - not_empty: wait when queue is empty (consumer side)
            - not_full:  wait when queue is full  (producer side)
    """

    def __init__(self, maxsize: int):
        if maxsize <= 0:
            raise ValueError("maxsize must be > 0")
        self._maxsize = maxsize
        self._queue = deque()
        self._lock = Lock()
        self._not_empty = Condition(self._lock)
        self._not_full = Condition(self._lock)

    def put(self, item):
        """
        Put an item into the queue.
        If the queue is full, block until space becomes available.
        """
        with self._not_full:
            while len(self._queue) >= self._maxsize:
                # Block producer when queue is full
                self._not_full.wait()

            self._queue.append(item)
            # Notify one waiting consumer that an item is available
            self._not_empty.notify()

    def get(self):
        """
        Remove and return an item from the queue.
        If the queue is empty, block until an item is available.
        """
        with self._not_empty:
            while len(self._queue) == 0:
                # Block consumer when queue is empty
                self._not_empty.wait()

            item = self._queue.popleft()
            # Notify one waiting producer that space is available
            self._not_full.notify()
            return item

    def qsize(self) -> int:
        """Return current size of the queue (non-blocking, approximate)."""
        with self._lock:
            return len(self._queue)

    def empty(self) -> bool:
        """Return True if the queue is empty."""
        return self.qsize() == 0

    def full(self) -> bool:
        """Return True if the queue is full."""
        with self._lock:
            return len(self._queue) >= self._maxsize
