import numpy as np

from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS

from .airsim_tools import AirSimTools

HELPER = AirSimTools()


class airsim(module):
    """
    The AirSim module is the class that handles all the AirSim setup
    """

    def _do_init(self):
        """
        This method initializes all the necessary AirSim configuration.
        """
        LOGGER.info(f"AirSim Do Init waiting for AirSim connection")
        HELPER.airsim_connect()
        HELPER.airsim_takeoff()

    async def _execute_step(self):
        """
        This method executes the AirSim step.
        """
        LOGGER.debug(f"AirSim Execute Step")
        rand_n = np.random.uniform(-100, 100)
        pose = HELPER.airsim_getpose()
        if HELPER.airsim_getcollision():
            raise Exception("Collision detected")
        if not HELPER.is_drone_moving():
            HELPER.move_to_point(x=2.0, y=rand_n, z=-10)

        message = {
            "x-pos": float(pose[0]),
            "y-pos": float(pose[1]),
            "z-pos": float(pose[2]),
            "speed": 5.0,
        }
        await NATS.send(self.__class__.__name__, message, "sionna")

    async def _callback(self, msg):
        """
        This method handles the AirSim callback.
        """
        LOGGER.debug(f"AirSim Callback")
        raise
