import logging


LOG_COLORS = {
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[97m",  # White
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[91m",  # Red
}

RESET_COLOR = "\033[0m"


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter to add colors to log messages based on log level.
    """

    def format(self, record):
        log_color = LOG_COLORS.get(record.levelname, "\033[97m")
        record.levelname = log_color + record.levelname + RESET_COLOR
        return super().format(record)


class logger(logging.Logger):

    """
    This class is used to create and manage logging.
    """

    def __init__(self, name="logger", log_level=logging.DEBUG):
        """
        Constructor that initializes the Log object.

        Parameters:
        log_level (int): The logging level.
        """

        super().__init__(name, log_level)
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter("[%(levelname)s] %(message)s"))
        self.addHandler(handler)
        self.setLevel(log_level)


LOGGER = logger()
