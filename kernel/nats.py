import asyncio

import nats as Nats

from .logger import LOGGER
from .process import PROCESS, subprocess


class nats:
    """
    This class is the NATS wrapper/do class.
    It is used for NATS initialization and message exchange.
    """

    __clients = {}
    __subscriptions = []
    __allowed_messages = []
    """
    All the NATS clients object.
    """

    def __init__(self):
        """
        Constructor that initializes the NATS object.
        """
        self.supress = True
        self.verbose = False
        pass

    async def send(self, module_name, msg, subject=""):
        encoded_msg = self.__encode(msg)
        if subject == "":  # <- IS_BROADCAST()
            nc = (await Nats.connect()).new_inbox()
        self.__clients[module_name].publish(subject, encoded_msg)
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

    def decode(self, msg, module_name=""):
        """
        This method decodes a message received from the NATS server.

        @param msg: The message to be decoded.
        """
        return self.__decode(msg, module_name)

    def __encode(self, msg):
        """
        This method encodes a message to be sent to the NATS server."""
        return str(msg).encode()

    def __decode(self, msg, module_name):
        """
        Basically, __decodes to retrieve the deserialized information, in format:
        [module_name, subject, message]. It also checks if the message is valid.

        @param msg: The message to be decoded.
        @param module_name: The module name to be decoded.

        @return: The deserialized information.
        """
        LOGGER.debug(f"Decoding message: {msg}")
        message = msg.data.decode()
        if self.__check_message(message, module_name):
            return [module_name, msg.subject, message]

    def __check_message(self, message, module_name):
        """
        This method checks if the message is a valid message.

        @param message: The message to be checked.
        @param module_name: The module name to be checked.

        @return: True if the message is valid, False otherwise.
        """
        return message in self.__allowed_messages[module_name]

    async def init_subscription(self, subscription, callback):
        """
        This method sets a NATS subscription to a specific module.

        @param subscription: The subscription to be set.

        * -> Prefix will be always `kernel`.
        * -> Afix will be the `module name`.
        * -> Sufix will be the `context` (mobility, AI, communications or 3D).

        @param callback: The callback to be called when a message is received.
        """
        self.__subscriptions.append(subscription)
        LOGGER.debug(f"Subscribing to \033[1m {subscription} \033[0m")
        nc = None
        await asyncio.sleep(
            0.5
        )  # __Really ugly__ hack to wait for the NATS server to start
        if str(subscription[2]) in self.__clients:
            LOGGER.debug(f"Using existing client")
            nc = self.__clients[str(subscription[2])]
        else:
            nc = await Nats.connect()
            self.__clients[str(subscription[2])] = nc

        await nc.subscribe(
            f"{subscription[2]}:{subscription[0]}.{subscription[1]}", cb=callback
        )
        await nc.flush()

    async def close_clients(self):
        """
        This method closes all the NATS clients.
        """
        for client in self.__clients.values():
            LOGGER.debug(f"Closing client {client}")
            await client.close()
        pass

    def allowed_messages(self, *messages):
        """
        This method sets the allowed messages for each module.
        So:

        module_name: [message_format1, message_format2, message_format3]

        @param messages: The messages to be allowed.
        """
        self.__allowed_messages = messages

    async def multicast(self, reference):
        nc = await Nats.connect()

        subjects = ["app.service1", "app.service2", "app.service3"]
        await asyncio.gather(*(nc.publish(subj, "EXECUTE") for subj in subjects))
        await nc.drain()


NATS = nats()
