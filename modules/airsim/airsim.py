import time

from kernel.logger import LOGGER
from kernel.module import module


class airsim(module):
    """
    The AirSim module is the class that handles all the AirSim setup
    """

    def _do_init(self):
        """
        This method initializes all the necessary AirSim configuration.
        """
        LOGGER.debug(f"AirSim Do Init")

    def execute_step(self):
        """
        This method executes the AirSim step.
        """
        pass

    async def _callback(self, msg):
        """
        This method handles the AirSim callback.
        """
        LOGGER.debug(f"AirSim Callback")
