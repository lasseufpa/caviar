from .scheduler import Scheduler


class Sync(Scheduler):
    """
    This class represents the synchronization for the simulation.
    """

    def __init__(self):
        """
        Constructor that initializes the Sync object.
        """
        super(Sync, self).__init__()

    def _encapsulate(self):
        pass
