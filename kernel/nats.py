import nats as Nats
import asyncio

from .logger import LOGGER
from .process import PROCESS, subprocess

class nats:
    """
    This class is the NATS wrapper/do class.
    It is used for NATS initialization and message exchange.
    """

    clients = {}
    subscriptions = []
    """
    All the NATS clients object.
    """

    def __init__(self):
        """
        Constructor that initializes the NATS object.
        """
        self.supress = False
        self.verbose = True
        pass

    def send(self):
        pass

    def init(self):
        """
        This method initializes the NATS server.
        """
        command = ["nats-server"]
        stdout = None
        stderr = None
        if self.supress:
            stdout = subprocess.DEVNULL
            stderr = subprocess.DEVNULL
        elif self.verbose:
            command.append("-DV")
        PROCESS.create_process(command, stdout=stdout, stderr=stderr)


    def receive(self):
        pass

    def __decode(self):
        pass

    def __encode(self):
        pass

    async def init_subscription(self, subscription, callback):
        """
        This method sets a NATS subscription to a specific module.

        @param subscription: The subscription to be set.
        """
        LOGGER.debug(f"Subscribing to {subscription[2]}:{subscription[0]}.{subscription[1]}")
        nc = None
        await asyncio.sleep(.5)
        if str(subscription[2]) in self.clients:
            LOGGER.debug(f"Using existing client")
            nc = self.clients[str(subscription[2])]
        else:
            nc = await Nats.connect()
            await nc.flush()
        self.clients[str(subscription[2])] = nc
        await nc.subscribe(f"{subscription[2]}:{subscription[0]}.{subscription[1]}", cb=callback
                                 )
        await asyncio.sleep(2)
        LOGGER.debug(f"Publishing to {subscription[2]}:{subscription[0]}.{subscription[1]}")
        await nc.publish(f"{subscription[2]}:{subscription[0]}.{subscription[1]}", b'Hello')
        LOGGER.debug(f"Published to {subscription[2]}:{subscription[0]}.{subscription[1]}")

    async def close_clients(self):
        """
        This method closes all the NATS clients.
        for client in self.clients.values():
            LOGGER.debug(f"Closing client {client}")
            try:
                await client.drain()
            except Exception as e:
                LOGGER.error(f"Error draining client {client}: {e}")
            finally:
                await client.close()

        """
        for client in self.clients.values():
            LOGGER.debug(f"Closing client {client}")
            await client.close()
        pass

NATS = nats()
