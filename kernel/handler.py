from .logger import LOGGER
from functools import wraps


def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            LOGGER.debug(f"Running {func.__name__}")
            return func(*args, **kwargs)
        except Exception as e:
            LOGGER.error(f"An error occurred in {func.__name__}: {e}")
            # Optionally, re-raise the exception if you want to propagate it
            # raise

    return wrapper
