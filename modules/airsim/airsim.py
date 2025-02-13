import time

from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS
import airsim as AIR
from .airsim_tools import AirSimTools

HELPER = AirSimTools()


class airsim(module):
    """
    The AirSim module is the class that handles all the AirSim setup
    """

    __client = None

    def _do_init(self):
        """
        This method initializes all the necessary AirSim configuration.
        """
        LOGGER.debug(f"AirSim Do Init")
        self.__client = HELPER.airsim_connect()
        LOGGER.info(f"AirSim client: {self.__client}")
        if self.__client is None:
            raise Exception("AirSim client is not connected")
        HELPER.airsim_takeoff(self.__client, uav_id=0)

    async def _execute_step(self):
        """
        This method executes the AirSim step.
        """
        LOGGER.debug(f"AirSim Execute Step")
        if self.__client is None:
            raise Exception("AirSim client is not connected")
        else:
            LOGGER.info(f"AirSim client is connected")
        message = {"x-pos": 32.0, "y-pos": 32.0, "z-pos": 20, "speed": 2.0}
        await NATS.send(self.__class__.__name__, message, "sionna")

    async def _callback(self, msg):
        """
        This method handles the AirSim callback.
        """
        LOGGER.debug(f"AirSim Callback")
