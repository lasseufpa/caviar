import asyncio
import os
from abc import ABC, abstractmethod

from .buffer import Buffer
from .handler import handler
from .logger import LOGGER
from .nats import NATS
from .process import PROCESS

LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(LOOP)


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
        self.buffer: Buffer = Buffer(
            10000
        )  # !< Buffer of the module (using size equal to 100 as default)
        self._lock = asyncio.Lock()
        self.loop = LOOP  # !< The event loop of the module

    @abstractmethod
    def _do_init(self):
        """
        This method initializes all the necessary module's configuration.
        """
        pass

    @abstractmethod
    async def _execute_step(self):
        """
        This method executes the module's step.
        * Mobility: Move, rotate, etc.
        * Communication: Calculate, send, receive, etc.
        * AI: Think, decide, process, etc.
        * 3D: Render, update, etc.
        """
        pass

    @handler.async_exception_handler
    async def __execute_step(self):
        """
        This method executes the module's step.
        """
        await self._execute_step()
        LOGGER.debug(f"Module {self.__class__.__name__} executed step")

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
        LOGGER.debug(f"Initializing {self.__class__.__name__.upper()} subscription")
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
        LOOP.run_until_complete(
            NATS.init_subscription(
                callback=self.__callback, module_name=self.__class__.__name__
            )
        )

    @handler.async_exception_handler
    async def __callback(self, msg):
        """
        This method is the internal message callback.
        It is responsible for calling the user-defined callback and setting the available flag.
        """
        msg = NATS.decode(msg, self.__class__.__name__)
        """
        @TODO: This is probably causing a soft-bug, since the callback could be innvoked
        multiple time by some module message. So the control message may be backpressured
        and the module will not be able to execute the step.
        """
        if msg is None:
            async with self._lock:
                await self.__execute_step()
            return
        LOGGER.debug(
            f"Module {self.__class__.__name__} received message: {msg} in subprocess {os.getpid()}"
        )
        self.buffer.add(msg)
        PROCESS.QUEUE.put(
            [self.__class__.__name__, True]
        )  # Notify the orchestrator that the module is ready to execute the step
