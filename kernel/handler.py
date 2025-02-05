import signal
import sys
import threading
import asyncio
from functools import wraps

from .logger import LOGGER
from .process import PROCESS
from .nats import NATS

SHT = threading.Event()


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
            SHT.set()
            __destroy()
            sys.exit(1)

    return wrapper


def __signal_handler(sig, frame):
    """
    This method handles the signal interrupt.
    """
    LOGGER.warning(f"Signal {sig} received")
    LOGGER.warning("Interrupt received, shutting down...")
    __destroy()
    sys.exit(1)


def __destroy():
    """
    This method destroys all threads.
    """
    LOGGER.debug("Destroying threads and subprocesses")
    #asyncio.run(NATS.close_clients())
    PROCESS.kill_processes()
    for thread in threading.enumerate():
        if thread is not threading.current_thread():
            LOGGER.debug(f"Joining thread {thread.name}")
            thread.join()
            if thread.is_alive():
                LOGGER.error(f"Thread {thread.name} did not terminate")
    LOGGER.debug("All threads terminated")
    sys.exit()


signal.signal(signal.SIGINT, __signal_handler)
