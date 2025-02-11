class Substep:
    """Class to encapsulate each substep of the simulation."""

    _next_id = 0
    _timeout = 0.0

    def __init__(self, ref):
        self._id = Substep._next_id
        Substep._next_id += 1
        self._reference = ref

    @property
    def reference(self):
        return self._reference

    @property
    def id(self):
        return self._id

    @property
    def timeout(self):
        return self._timeout

    def __str__(self):
        return f"substep(id={self._id}, reference={self._reference})"

    def __repr__(self):
        return str(self)
