from .logger import LOGGER


class Step:
    """Class to encapsulate each step of the simulation."""

    _next_id = 0
    _timeout = 0

    def __init__(self, *substeps):
        self._id = Step._next_id
        Step._next_id += 1
        self._substeps = substeps

    @property
    def steps(self):
        return self._substeps

    @property
    def timeout(self):
        return self._timeout

    @property
    def step_id(self):
        return self._id

    def __str__(self):
        return f"Step(id={self._id}, steps={self._substeps})"

    def __repr__(self):
        return str(self)

    @classmethod
    def create(cls, *substeps):
        """
        Class method to create a new Step instance and return it as a dictionary.
        """
        instance = cls(*substeps)
        return {"ID": instance._id, "substeps": instance._substeps}

    def get_substeps(self):
        """
        Method to return the substeps of the step.
        """
        return self._substeps
