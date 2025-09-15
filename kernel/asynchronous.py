from .execute import ExecuteStep
from .logger import LOGGER
from .process import PROCESS
from .scheduler import Scheduler
from .step import Step
from .substep import Substep


class Async(Scheduler):
    """
    This class represents the asynchronous simulation.
    In a asynchronous simulation, the modules are executed in
    parallel where all are encapsulated in a substep, and consequently in a step.
    Since, the message passing is done in a asynchronous way, the modules will always
    execute with (t-1) messages.

    +---------+
    | Step 1
    | +-----+
    | | s1  |
    | +-----+
    | +-----+
    | | s2  |
    | +-----+
    | +-----+
    | | s3  |
    | +-----+
    +---------+


    """

    __allowed_substeps = []
    __encapsulated = None

    def __init__(self, interval: float):
        """
        Constructor that initializes the Async object.

        @param interval: The time interval of the simulation.
        """
        super(Async, self).__init__(interval)

    def _encapsulate(self):
        """
        This method encapsulates the substeps of the simulation.
        """
        if self.__allowed_substeps:
            self.__encapsulated = Step(*self.__allowed_substeps)

    def __check__allowance(self):
        """
        This method checks if there is available input in all enabled modules
        """
        LOGGER.debug("Checking allowance...")
        available_modules = PROCESS.check_state()
        for module_dict in self._modules:
            for reference, dependency in module_dict.items():
                if not dependency:
                    """
                    If the module has no dependencies, it is allowed to run
                    """
                    self.__allowed_substeps.append(Substep(reference))
                    continue
                LOGGER.debug(f"Checking module {reference}...")
                if available_modules and reference in available_modules:
                    """
                    If the module is not allowed, the execute step will be skipped
                    """
                    LOGGER.debug(f"Module {reference} is allowed.")
                    self.__allowed_substeps.append(Substep(reference))
        LOGGER.debug(f"Allowed modules to run in Event: {self.__allowed_substeps}")

    async def _execute_step(self):
        """
        This method executes the step of the simulation.
        """
        self.__check__allowance()
        if self.__allowed_substeps:
            self._encapsulate()
            LOGGER.debug(f"Allowed to walk {self.__allowed_substeps}")
            await ExecuteStep.execute_step(self.__encapsulated)
            self.__clean__allowed_substeps()

    def __clean__allowed_substeps(self):
        """
        This method cleans the allowed substeps.
        """
        self.__allowed_substeps.clear()
        LOGGER.debug("Allowed substeps cleaned.")
