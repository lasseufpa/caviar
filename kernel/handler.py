import os
import signal
import sys
import threading
import asyncio
from functools import wraps

from .logger import LOGGER
from .process import PROCESS
from .nats import NATS

class handler:

    """
    This class is responsible for handling signals and exceptions.
    """

    @staticmethod
    def exception_handler(func):
        """
        This decorator handles exceptions (errors) in the functions.
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                LOGGER.debug(f"Running {func.__name__}")
                return func(*args, **kwargs)
            except Exception as e:
                LOGGER.error(f"An error occurred in {func.__name__}: {e}")
                handler.__destroy()
                sys.exit(1)

        return wrapper

    @staticmethod
    def __signal_handler(sig, frame):
        """
        This method handles the signal interrupt.
        """
        if getattr(handler.__signal_handler, "called", False):
            return
        handler.__signal_handler.called = True
        # LOGGER.warning(f"SIGTERM received in {frame}")
        LOGGER.warning(f"SIGTERM received")
        handler.__destroy()
        sys.exit(1)

    @staticmethod
    def __destroy():
        """
        This method destroys all threads.
        """
        if getattr(handler.__destroy, "called", False):
            return
        asyncio.run(NATS.close_clients())
        handler.__destroy.called = True
        LOGGER.debug(f"Destroying subprocess: {PROCESS.processes}")
        PROCESS.kill_processes()
        for thread in threading.enumerate():
            if thread is not threading.current_thread():
                LOGGER.debug(f"Joining thread {thread.name}")
                thread.join(timeout=1)
                if thread.is_alive():
                    LOGGER.warning(f"Perhaps, {thread.name} did not terminate")
        LOGGER.debug("All threads terminated")
        sys.exit(0)

    @staticmethod
    def __subprocess_handler(_, __):
        if getattr(handler.__subprocess_handler, "called", False) or getattr(
            handler.__signal_handler, "called", False
        ):
            return
        handler.__subprocess_handler.called = True
        """
        This method handles the subprocess signal.
        """
        LOGGER.error(f"Something went wrong in subprocess...")
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)
        handler.__destroy()
        sys.exit(1)

    @staticmethod
    def subprocess_handler(func):
        """
        This decorator handles the subprocess signal.
        """
        if getattr(handler.__signal_handler, "called", False):
            return

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                LOGGER.error(f"An error occurred in {func.__name__}: {e}")

        return wrapper

    @staticmethod
    def register_signals():
        """
        This method registers the signals.
        """
        if getattr(handler.register_signals, "called", False):
            return
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, handler.__signal_handler)
            signal.signal(signal.SIGTERM, handler.__signal_handler)
            # TODO: Maybe __signal.pthread_sigmask(signal.SIG_BLOCK, [signal.SIGCHLD])__ is better.
            # Since, we are working with multiple threads and subprocesses, we need to block the SIGCHLD
            # signal to avoid the creation of zombie processes.
            signal.signal(signal.SIGCHLD, handler.__subprocess_handler)

    @staticmethod
    def callback_handler(func):
        """
        This decorator handles exceptions (errors) in the functions.
        """

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                LOGGER.debug(f"Running {func.__name__}")
                return await func(*args, **kwargs)
            except Exception as e:
                LOGGER.error(f"An error occurred in {func.__name__}: {e}")
                # Since the callback possible errors will not occur in the main thread, we need to kill
                # all the processes using the SIGTERM signal to avoid zombie processes.
                os.kill(os.getpid(), signal.SIGTERM)
                sys.exit(1)

        return async_wrapper
