import copy

from .execute import ExecuteStep
from .logger import LOGGER
from .process import PROCESS
from .scheduler import Scheduler
from .step import Step
from .substep import Substep


class Sync(Scheduler):
    """
    This class represents the synchronization for the simulation.
    """

    __allowed_substeps = []
    __encapsulated = None

    def __check__allowance(self):
        """
        This method checks if there is available input in all enabled modules.
        As default, all modules are allowed to run in synchronous mode.
        """
        LOGGER.debug("Checking allowance...")
        for module_dict in self._modules:
            for reference, dependency in module_dict.items():
                LOGGER.debug(f"Module added to run {reference}...")
                self.__allowed_substeps.append(Substep(reference))

    def __init__(self, interval: float):
        """
        Constructor that initializes the Sync object.

        @param interval: The time interval of the simulation.
        """
        super(Sync, self).__init__(interval)

    def _encapsulate(self):
        """
        In syncrhonous case, encapsulation is done for *each* substep,
        assuming multiple substeps as steps in a single event.
        """
        self.__encapsulated = []
        if self.__allowed_substeps:
            for substep in self.__allowed_substeps:
                LOGGER.debug(f"Encapsulating substep: {substep}")
                self.__encapsulated.append(Step(*[substep]))

    async def _execute_step(self):
        """
        This method executes the step of the simulation.
        """
        all_modules: dict = copy.deepcopy(self._modules[0])
        count = 0
        LOGGER.debug(f"All modules to run: {all_modules}")
        while all_modules:
            for reference in list(all_modules.keys()):
                if not all_modules[reference]:
                    substep = Substep(reference)
                    step = Step(*[substep])
                    await ExecuteStep.execute_step(step)
                    all_modules.pop(reference)
                    LOGGER.debug(
                        f"Module {reference} ran and now are removed from the list: {all_modules}"
                    )
                else:
                    modules_state = PROCESS.check_state()
                    if not modules_state:
                        count += 1
                        LOGGER.debug(f"No modules available: {modules_state}")
                        await self._wait(1)
                        if count > 5:
                            LOGGER.error("No modules available to run. Exiting...")
                            count = 0
                            return
                    else:
                        LOGGER.debug(f"Modules available: {modules_state}")
                        if reference in modules_state:
                            substep = Substep(reference)
                            step = Step(*[substep])
                            await ExecuteStep.execute_step(step)
                            all_modules.pop(reference)
                            # all_modules.remove(module_dict)

    def __clean__allowed_substeps(self):
        """
        This method cleans the allowed substeps.
        """
        self.__allowed_substeps.clear()
        LOGGER.debug("Allowed substeps cleaned.")
