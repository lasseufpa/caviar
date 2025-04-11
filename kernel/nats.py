import asyncio
import json

import nats as Nats

from .logger import LOGGER, logging
from .process import PROCESS, subprocess

logging.getLogger("nats").setLevel(logging.CRITICAL)  # Suppress NATS logs


class nats:
    """
    This class is the NATS wrapper/do class.
    It is used for NATS initialization and message exchange.
    """

    __clients = {}
    __allowed_messages = {}
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

    async def send(self, module_name, msg, subject):
        """
        This method sends a message to the NATS server in a specific subject.

        @param module_name: The name of the module that sends the message.
        @param msg: The message to be sent.
        @param subject: The subject to send the message (mostly the module's name which will receive the message).
        """
        message = {module_name: msg}
        encoded_msg = self.__encode(message)
        full_subject = "kernel." + subject
        LOGGER.debug(f"Sending message: {message} to {full_subject}")
        await self.__clients[module_name].publish(full_subject, encoded_msg)

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
        @return: The decoded information.
        """
        return self.__decode(msg, module_name)

    def __encode(self, msg):
        """
        This method encodes a message to be sent to the NATS server.
        Here, always use JSON to serialize the message."""
        return json.dumps(msg).encode()

    def __decode(self, msg, module_name):
        """
        Basically, __decodes to retrieve the deserialized information, in format:
        [subject, message]. It also checks if the message is valid.
        Moreover, control messages are also decoded and returned.

        @param msg: The message to be decoded.
        @param module_name: The module name to be decoded.
        @return: The deserialized information.
        """
        LOGGER.debug(f"Decoding message: {msg}")
        message = msg.data
        if message == b"\00":
            return
        message_decoded = json.loads(message.decode())
        LOGGER.debug(f"Decoded message: {message_decoded}")
        if self.__check_message(message_decoded, module_name):
            return [msg.subject, message_decoded]
        else:
            raise ValueError(
                f"Message {message_decoded} is not an allowed message for {module_name}"
            )

    def __check_message(self, message, module_name):
        """
        This method checks if the message is a valid message.
        Here it checks if the message has the same keys as the allowed messages.

        @param message: The message to be checked in JSON format.
        @param module_name: The receiver module name.
        @return: True if the message is valid, False otherwise.
        """
        LOGGER.debug(
            f"Checking message: {message} for {module_name} in {self.__allowed_messages[module_name]}"
        )
        if module_name not in self.__allowed_messages:
            LOGGER.debug(
                f"Module {module_name} not in allowed messages: {self.__allowed_messages}"
            )
            return False
        else:
            for key in message.keys():
                message_keys = set(message[key].keys())
                allowed_keys = set(self.__allowed_messages[module_name][key])
                if not message_keys.issubset(allowed_keys):
                    LOGGER.debug(
                        f"Key {key} not in allowed messages: {self.__allowed_messages[module_name][key]}"
                    )
                    return False
        return True

    async def init_subscription(self, callback, module_name=""):
        """
        This method sets a NATS subscription to a specific module.

        @param subscription: The subscription to be set.

        * Prefix will be always `kernel`
        * Afix will be the `module name`
        @param callback: The callback to be called when a message is received.
        """
        subscription = "kernel." + module_name
        LOGGER.debug(f"Subscribing to \033[1m {subscription} \033[0m")

        await asyncio.sleep(
            0.5
        )  # __Really ugly__ hack to wait for the NATS server to start

        nc = None
        if module_name in self.__clients:
            LOGGER.debug(f"Using existing client")
            nc = self.__clients[module_name]
        else:
            nc = await Nats.connect()
            self.__clients[module_name] = nc

        await nc.subscribe(subscription, cb=callback)
        await nc.flush()

    async def close_clients(self):
        """
        This method closes all the NATS clients.
        """
        for client in self.__clients.values():
            LOGGER.debug(f"Closing client {client}")
            await client.close()
        pass

    def allowed_messages(self, messages: dict):
        """
        This method sets the allowed messages for each module.
        So:

        module_name: [message_format1, message_format2, message_format3]

        @param messages: The expected messages for each module.
        """
        LOGGER.debug(f"Setting allowed messages: {messages}")
        self.__allowed_messages = messages

    async def multicast(self, references, message=""):
        """
        This method multicasts a message to all the references.
        The multicast is done by sending the message to all the subjects
        that are in the references list.
        The subjects are in the format kernel.<reference>.
        The multicast will perform concurrently the send to all the references.
        This is done by using asyncio.gather to execute the send in parallel.

        @param references: The references to be sent.
        @param message: The message to be sent.
        """
        nc = await Nats.connect()
        LOGGER.debug(f"Multicasting to {references}")
        subjects = [f"kernel.{reference}" for reference in references]
        if not message:
            message = b"\00"
        """
        Executes it in parallel, almost in the same time (concurrently)
        """
        await asyncio.gather(*(nc.publish(subj, message) for subj in subjects))
        await nc.drain()


NATS = nats()
