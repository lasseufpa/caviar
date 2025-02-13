import time
from abc import ABC, abstractmethod

from .handler import handler
from .logger import LOGGER


class Scheduler(ABC):
    """
    This class represents the scheduler for the simulation.
    """

    _event = 0
    _modules = None
    """The enabled modules of the simulation."""

    def __init__(self):
        """
        Constructor that initializes the Scheduler object.
        """
        pass

    @handler.exception_handler
    def __wait(self, timeout=0.2):
        """
        This method waits for a certain amount of time.

        @param timeout: The amount of time to wait.
        """
        time.sleep(timeout)

    @abstractmethod
    def _encapsulate(self):
        """
        This method encapsulates the substeps of the simulation.
        """
        pass

    @abstractmethod
    def _execute_step(self):
        """
        This method executes the step of the simulation.
        """
        pass

    @handler.exception_handler
    def execute_steps_in_loop(self):
        """
        This method executes the steps in a loop.
        """
        # while True:
        LOGGER.info("Executing steps...")
        while True:
            LOGGER.debug(f"Event_id: {self._event}")
            self._execute_step()
            self.__wait(15)
            # if self._stop_condition():
            #    break
            self._event += 1

    # @handler.exception_handler
    def update_modules(self, *modules):
        """
        This method updates the enabled modules of the simulation.

        @param modules: The enabled modules of the simulation.
        """
        self._modules = modules
