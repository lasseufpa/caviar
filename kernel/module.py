import asyncio
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path

from .handler import handler
from .logger import LOGGER
from .nats import NATS
from .process import PROCESS

LOOP = asyncio.get_event_loop()


class module(ABC):
    """
    This class is the base class for all modules.
    The module class can't have an __init__ method, since the orchestrator initializes it.
    Use do_init instead, to intialize your module.
    """

    def __init__(self):
        """
        Constructor that initializes the module object.
        """
        LOGGER.debug(
            f"Module {self.__class__.__name__} created with instance ID: {id(self)}"
        )
        pass

    @abstractmethod
    def _do_init(self):
        """
        This method initializes all the necessary module's configuration.
        """
        pass

    @abstractmethod
    async def execute_step(self):
        """
        This method executes the module's step.
        * Mobility: Move, rotate, etc.
        * Communication: Calculate, send, receive, etc.
        * AI: Think, decide, process, etc.
        * 3D: Render, update, etc.
        """
        pass

    def initialize(self):
        """
        This method initializes the module.
        """

        """
        @TODO: I think subscribing should be done first, since, for some reason, the module
        may need to send some message to be initialized. This is kind of a _async_ dependency
        but yeah I need to think more about this.
        """
        self._do_init()
        LOGGER.debug(
            f"Initializing {self.__class__.__name__.upper()} subscription"
        )
        self.__init_subscription()

        """
        @TODO: Maybe (and just maybe) we should use NATS to check if the module is ready"""
        PROCESS._child_conn.send("")  # empty string just to flag the process as ready

        # Use run_forever here is not a big deal, since this is a subprocess and when
        # it is killed, it will be destroyed too.
        LOOP.run_forever()

    def __init_subscription(self):
        """
        This method initializes the module's subscription.
        """
        LOOP.run_until_complete(NATS.init_subscription(callback=self.__callback, module_name=self.__class__.__name__))
    
    @handler.callback_handler
    async def __callback(self, msg):
        """
        This method is the internal message callback.
        It is responsible for calling the user-defined callback and setting the available flag.
        """
        msg = NATS.decode(msg, self.__class__.__name__)
        LOGGER.debug(
            f"Module {self.__class__.__name__} received message: {msg} in subprocess {os.getpid()}"
        )
        PROCESS.QUEUE.put([self.__class__.__name__, True])
        await self._callback(msg)

    @abstractmethod
    async def _callback(self, msg):
        """
        This method is the callback for the subscription.
        Here, the user can define the behavior of the module when a message is received.
        """
        pass
