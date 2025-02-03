from kernel.logger import LOGGER
from kernel.module import module


class sionna(module):
    """
    The Sionna module is the class that handles all the Sionna setup
    """

    def __init__(self):
        """
        Constructor that initializes the Sionna object.
        """
        pass

    def do_init(self):
        """
        This method initializes all the necessary Sionna configuration.
        """
        LOGGER.debug(f"Sionna Do Init")
        pass

    def execute_step(self):
        """
        This method executes the Sionna step.
        """
        pass
