import numpy as np
import rdp

from .buffer import Buffer
from .logger import LOGGER


class IdealBuffer(Buffer):
    """
    The idea is to perform an ideal method where each new item will
    never be blocked by the previous items. This is achieved by
    performing a granularity check before adding other item to the buffer.

    In the _Ideal_ buffer, it is assumed that the data is correlated in TIME
    and not exactly in space. I.e., the buffer performs

    """

    __cursor: int = (
        0  # !< Cursor of the buffer (saves where the buffer will start being filled),
        # this means that the dump method will perform [cursor:len(buffer)]
    )

    def __init__(self, size: int):
        """
        @TODO: Maybe it should be a personalized sionna buffer.
        Constructor that initializes the buffer object.
        """
        super().__init__(size)

    def add(self, item, treshold=0.01):
        """
        Basically, to add a new item in this context, we should first check
        if the buffer is full. If it is, we should dump the buffer.
        After perform the "clean" method, we are able to add the items
        in the buffer.

        The added elements are only the ones that are not similar to the last
        element in the buffer. The similarity is defined by the Euclidian
        distance between the last element in the buffer and the new item.
        """
        item = self.__transform_to_buffer_item(item)
        LOGGER.debug("Report buffer condition: %s", self.__len__())
        if self.is_full():
            self.dump()

        if not self.is_empty():
            last_item = self.buffer.queue[-1][0]
            # Perform Euclidian distance
            diff = np.linalg.norm(np.array(item) - np.array(last_item))

            if diff < treshold:
                LOGGER.debug(
                    f"Item {item} is too similar to the last item {last_item}, ignoring it."
                )
                return
        super().add(item)

    def dump(self, epsilon=0.1, algorithm="iter"):
        """
        Attempt to dump the buffer. This method will perform the RDP algorithm
        to remove the redundant points in the buffer.
        The RDP algorithm tries to condense the points of a curve
        by removing the points that are not significant (i.e. the points
        that are not needed to define the curve).
        """
        is_2d = True
        points = np.array([item[0] for item in self.buffer.queue])
        n_windows, window_length = self._get_n_windows()
        if points.ndim == 1:
            points = [
                [float(points[i]), i] for i in range(len(points))
            ]  # Ensure 2D array to avoid rdp error
            is_2d = False

        def nd_dist(p, s, e):
            """
            Internal function to calculate the distance between a point and a segment
            """
            if np.allclose(s, e):
                return np.linalg.norm(p - s)
            else:
                se = e - s
                t = np.dot(p - s, se) / np.dot(se, se)
                t = np.clip(t, 0, 1)
                proj = s + t * se
                return np.linalg.norm(p - proj)

        # Perform RDP only on new points (from __cursor onwards)
        simplified = []
        for i in range(n_windows):
            start = self.__cursor + i * window_length
            end = (
                self.__cursor + (i + 1) * window_length
                if i < n_windows - 1
                else len(points)
            )
            window = points[start:end]
            if len(window) >= 2:
                simplified.extend(
                    rdp.rdp(
                        window,
                        epsilon=epsilon,
                        algo=algorithm,
                        dist=nd_dist,
                    )
                )

        preserved = list(self.buffer.queue)[: self.__cursor]
        self.clean()
        for item in preserved:
            super().add(item[0])
        for item in simplified:
            if not is_2d:
                item = item[0]
            super().add(item)

        self.__cursor = self.__len__()

    def get(self):
        if self.__cursor > 0:
            self.__cursor -= 1
        return super().get()

    def _get_n_windows(self, k=1.0, N_min=1, N_max=1024):
        """
        Internal function to get the number of windows

        @param k: The factor to multiply the number of windows
        @param N_min: The minimum number of windows
        @param N_max: The maximum number of windows
        @return: The number of windows
        """
        intervals = (
            np.diff([item[1] for item in list(self.buffer.queue)[self.__cursor :]])
            / 1e9
        )  # Get intervals only in non-processed data
        mean_grn = np.mean(intervals)
        ref_grn = np.median(intervals)
        n_windows = int(k * ref_grn / mean_grn)
        n_windows = np.clip(n_windows, N_min, N_max)
        window_length = len(self.buffer.queue) // n_windows
        return n_windows, window_length

    def __transform_to_buffer_item(self, msg):
        """
        This method transforms the message to a buffer item.

        item is only the parameters of the message, without the _header_.
        The item is a list.

        @param msg: The message to be transformed.
        @return: The transformed message.

        @TODO: MAKE THIS ROBUST or crash the system if the message is not in the expected format.
        """
        if not isinstance(msg, list):
            raise TypeError(f"Message is not a list. It is {type(msg)}")
        if isinstance(msg[1], dict):
            buffer_item = list(list(msg[1].values())[0].values())
            return buffer_item

    def fill(self):
        pass
