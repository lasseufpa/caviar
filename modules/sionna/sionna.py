from kernel.logger import LOGGER
from kernel.module import module

import sionna.rt as RT

class sionna(module):
    """
    The Sionna module is the class that handles all the Sionna setup
    """
    
    def _do_init(self):
        """
        This method initializes all the necessary Sionna configuration.
        """
        #RT.load_scene()
        #RT.PathSolver()
        LOGGER.debug(f"Sionna Do Init")

    async def _execute_step(self):
        """
        This method executes the Sionna step.
        """
        LOGGER.debug(f"------> Sionna Execute Step")
        pass

    async def _callback(self, msg):
        """
        This method handles the Sionna callback.
        """
        LOGGER.debug(f"Sionna Callback")
        pass
