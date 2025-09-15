from kernel.module import module
from kernel.logger import LOGGER
from kernel.nats import NATS

class bob(module):
    """
    The Bob module is a dumb module that does nothing.
    It only serves as an example of how to create a module,
    send and receive messages.
    It can be used to test the co-simulation framework.
    """

    def _do_init(self):
        """
        This method initializes all the necessary configuration. 
        Think of it as the constructor of the module (because it actually is).
        Bob is dependent to Alice, so it will receive messages, and will execute
        its own logic, respecting the orchestrator's time step and the Alice's output.
        No one is expecting anything from Bob, so it will not send any message.

        @NOTE: It is important to understand that this method is called only once, and no
        event loop is running yet. So, you cannot use async methods here or even schedule events.
        Do this in execute_step instead.
        """
        LOGGER.info(f"Bob Init: Here is where the initialization happens.")

    async def _execute_step(self):
        """
        This method is called at every step of the simulation.
        It is an async method, so you can use await here.

        Look the message order: the first element in buffer list is the item, the second is the time
        whether the message was transmitted. The second element of the result is the message itself,
        the first is the module's name that sent the message. So now you can simply capture the dict message
        """
        LOGGER.info(f"Bob received message: {self.buffer.get()[0][1]['alice']['message']}")