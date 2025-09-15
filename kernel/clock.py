import time


class Clock:
    """
    Clock class that handles the simulation time.
    """

    def __init__(self, interval: float):
        """
        Constructor that initializes the Clock object.

        @param interval: The time interval of the simulation.
        """
        self._start_time = time.time_ns()
        self.__time_stamp = interval

    def get_step_time(self):
        """
        This method returns the time stamp of the simulation.
        """
        return self.__time_stamp

    def get_simulation_time(self):
        """
        This method returns the simulation time.

        @NOTE: This is not exactly the time that passed in each simulator,
        but the time that passed in the co-simulation, from the orchestrator
        perspective.
        """
        return (time.time_ns() - self._start_time) / 1e9
