import os

from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS
from kernel.process import PROCESS

class ns3(module):
    def _do_init(self):
        """
        This method initializes all the necessary ns3 configuration.
        """
        LOGGER.debug(f"ns3 Do Init")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if not os.path.exists(dir_path + "/ns-3-dev"):
            raise ValueError("ns3 should be installed. Please do: git submodule update --init --recursive")
        command = "ns3 run --enable-sudo rt-tap-bridge"
        PROCESS.create_process(command)
        pass

    async def _execute_step(self):
        """
        This method executes the ns3 step.
        """
        pass
