import time

from kernel.logger import LOGGER
from kernel.module import module


class airsim(module):
    """
    The AirSim module is the class that handles all the AirSim setup
    """

    def __init__(self):
        """
        Constructor that initializes the AirSim object.
        """
        pass

    def do_init(self):
        """
        This method initializes all the necessary AirSim configuration.
        """
        LOGGER.debug(f"AirSim Do Init")
        time.sleep(5)
        pass

    def execute_step(self):
        """
        This method executes the AirSim step.
        """
        pass
