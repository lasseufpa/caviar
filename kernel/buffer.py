import time
from abc import ABC, abstractmethod
from queue import Queue

import numpy as np

from .logger import LOGGER


class Buffer(ABC):
    """
    The Buffer class is the most primitve circular buffer that stores elements in a queue.
    It has a fixed size and when it is full, the oldest element is removed.
    It also calculates the granularity of the elements in the buffer.

    If the calculated granularity is None, it means that the buffer is empty or has only one element.
    The granularity is calculated using the mean of the time intervals between the elements in the buffer.
    The granularity is calculated asynchronously to avoid blocking the main process.
    Also, if the the calculated granularity is high (big sample time inverval), it means
    that the item "producer" is not fast enough and the buffer is not being filled. On the other hand,
    if the granularity is low (small sample time interval), it means that the "item" producer is fast enough
    and the buffer is being filled. The granularity should be handled properly in the buffer manager.
    """

    def __init__(self, size: int):
        self.size = size  #!< Size of the buffer
        self.buffer: Queue = Queue(maxsize=size)  #!< Buffer of the module
        self.grn: float = None  #!< Granularity of the buffer in a given time interval in samples per second

    # async
    def granularity(self, cursor=0):
        """
        Get the granularity of elements interval in the buffer.
        Each element of the buffer is a list containing the element and the time it was added.
        The granularity is the mean of the time intervals between the elements in the buffer.

        This method is asynchronous to avoid blocking the main process.
        """
        with self.buffer.mutex:
            queue_list = self.buffer.queue[cursor:]
        if len(queue_list) > 2:
            intervals = [
                queue_list[i + 1][1] - queue_list[i][1]
                for i in range(len(queue_list) - 1)
            ]
            self.grn = 1e9 / np.mean(intervals)
        LOGGER.debug(
            f"Buffer granularity: {self.grn} samples per second, buffer size: {len(queue_list)}"
        )

    def _add(self, item):
        """
        Add an item to the buffer. If the buffer is full, remove the oldest item.

        @param item: The item to be added to the buffer.
        """
        if self.buffer.full():
            LOGGER.warning(f"Buffer full, removing oldest item: {self.buffer.queue[0]}")
            self.buffer.get()
        self.buffer.put([item, time.time_ns()])

    def get(self):
        """
        Get an item from the buffer. If the buffer is empty, return None.
        """
        return self.buffer.get()

    def is_empty(self):
        """
        Check if the buffer is empty.
        """
        return self.buffer.empty()

    def is_full(self):
        """
        Check if the buffer is full.
        """
        return self.buffer.full()

    def __len__(self):
        """
        Get the length of the buffer.
        """
        return self.buffer.qsize()

    def clean(self):
        """
        Clean the buffer.
        """
        while not self.buffer.empty():
            self.buffer.get()

    def get_granularity(self):
        """
        Get the granularity of the buffer.
        """
        return self.grn

    def get_buffer(self):
        """
        Get the buffer.
        """
        return self.buffer.queue

    @staticmethod
    def dump(self):  # , *args
        """
        Use some method to dump the buffer. I.e., use some method to
        avoid full buffering.

        """
        pass

    @staticmethod
    def fill(self):  # , *args
        """
        Use some method to fill the buffer. I.e., use some method to
        avoid empty buffering.

        """
        pass
