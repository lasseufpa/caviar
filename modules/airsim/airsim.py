import time

from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS


class airsim(module):
    """
    The AirSim module is the class that handles all the AirSim setup
    """

    def _do_init(self):
        """
        This method initializes all the necessary AirSim configuration.
        """
        LOGGER.debug(f"AirSim Do Init")

    async def _execute_step(self):
        """
        This method executes the AirSim step.
        """
        LOGGER.debug(f"AirSim Execute Step")
        message = {"x-pos": 32.0, "y-pos": 32.0, "z-pos": 20, "speed": 2.0}
        await NATS.send(self.__class__.__name__, message, "sionna")

    async def _callback(self, msg):
        """
        This method handles the AirSim callback.
        """
        LOGGER.debug(f"AirSim Callback")
