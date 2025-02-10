from .logger import LOGGER
from .process import PROCESS
from .scheduler import Scheduler
from .step import Step
from .substep import Substep


class Async(Scheduler):
    """
    This class represents the asynchronous simulation.
    +---------+
    | Event 1 |
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

    def __init__(self):
        """
        Constructor that initializes the Async object.
        """
        super(Async, self).__init__()

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
        for module_dict in self._modules:
            for module_name, _ in module_dict.items():
                LOGGER.debug(f"Checking module {module_name}...")
                if PROCESS.check_state(module_name):
                    """
                    If the module is not allowed, the execute step will be skipped
                    """
                    LOGGER.debug(f"Module {module_name} is allowed.")
                    # self.__allowed_substeps.append(Substep())
        LOGGER.debug(f"Allowed modules to run in Event: {self.__allowed_substeps}")

    def _execute_step(self):
        """
        This method executes the step of the simulation.
        """
        self.__check__allowance()
        if self.__allowed_substeps:
            self._encapsulate()
            self.__clean__allowed_substeps()
        # ExecuteStep()

    def __clean__allowed_substeps(self):
        """
        This method cleans the allowed substeps.
        """
        self.__allowed_substeps.clear()
        LOGGER.debug("Allowed substeps cleaned.")
