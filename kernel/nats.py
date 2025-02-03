from pynats import NATSClient

from .process import PROCESS, subprocess


class nats:
    """
    This class is the NATS wrapper/do class.
    It is used for NATS initialization and message exchange.
    """

    def __init__(self):
        """
        Constructor that initializes the NATS object.
        """
        self.supress = True
        self.verbose = False
        pass

    def send(self):
        pass

    def init(self, ip="127.0.0.1"):
        """
        This method initializes the NATS server.
        """
        command = ["nats-server"]
        stdout = None
        stderr = None
        if self.supress:
            stdout = subprocess.DEVNULL
            stderr = subprocess.DEVNULL
        elif self.verbose:
            command.append("-DV")
        PROCESS.create_process(command, stdout=stdout, stderr=stderr)
        NATSClient().connect()

    def receive(self):
        pass

    def __decode(self):
        pass

    def __encode(self):
        pass
