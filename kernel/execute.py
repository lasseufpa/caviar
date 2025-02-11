from .logger import LOGGER


class ExecuteStep:
    """
    This class is responsible for executing the step of the simulation.
    """

    def __init__(self, step):
        """
        Constructor that initializes the ExecuteStep object.
        """
        deserialized_references = self.__deserialize(step)
        self.__execute_step(deserialized_references)

    def __deserialize(self, step):
        """
        This method deserializes the step of the simulation.
        It basically retrieves the sub_steps references to trigger the
        module.__execute_step.

        @param step: The step to be deserialized.

        @return: The deserialized step -> List.
        """
        LOGGER.debug(f"Deserializing {step}")
        sub_steps = step.get_substeps()
        # @TODO: check if it is necessary to return the id of the substep
        return [substep.reference for substep in sub_steps]

    def __execute_step(self, references):
        """
        This method executes the step of the simulation.

        @param references: A list of references to _module.execute_step_
        """
