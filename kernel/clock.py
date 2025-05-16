import time


class Clock:
    """
    Clock class that handles the simulation time.
    """

    def __init__(self):
        """
        Constructor that initializes the Clock object.
        """
        self._start_time = 0
        self.__time_stamp = 0.00010  # 0.01

    def get_step_time(self):
        """
        This method returns the time stamp of the simulation.
        """
        self._start_time += self.__time_stamp  # 0.01
        return self.__time_stamp

    def get_simulation_time(self):
        """
        This method returns the simulation time.
        """
        return self._start_time
