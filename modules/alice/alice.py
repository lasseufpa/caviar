from kernel.module import module
from kernel.logger import LOGGER
from kernel.nats import NATS

class alice(module):
    """
    The Alice module is a dumb module that does nothing.
    It only serves as an example of how to create a module,
    send and receive messages.
    It can be used to test the co-simulation framework.
    """

    def _do_init(self):
        """
        This method initializes all the necessary configuration. 
        Think of it as the constructor of the module (because it actually is).
        Alice is independent to Bob, so it will not receive any message, and will execute
        only its own logic, respecting the orchestrator's time step.
        
        @NOTE: It is important to understand that this method is called only once, and no
        event loop is running yet. So, you cannot use async methods here or even schedule events.
        Do this in execute_step instead.
        """
        LOGGER.info(f"Alice Init: Here is where the initialization happens.")
        self._message = {"message": "Hello from Alice!"}

    async def _execute_step(self):
        """
        This method is called at every step of the simulation.
        It is an async method, so you can use await here.
        """
        LOGGER.info(f"Alice is sending a message to Bob.")
        await NATS.send(self.__class__.__name__, self._message, "bob")