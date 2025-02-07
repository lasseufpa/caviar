import os
import signal
import subprocess
from multiprocessing import Pipe, Process

from .logger import LOGGER


class process(Process):
    """
    This class is responsible for processes management.

    @TODO: Check if it is necessary to be a subclass of Process. Because this class is not being used as a PROCESS.
    We are using the subprocess module to >create< and >manage< processes.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor that initializes the Process object.
        """
        # super().__init__(*args, **kwargs)
        self._parent_conn, self._child_conn = Pipe()
        self.processes = []

    def create_process(
        self, command, *args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, wait=False
    ):
        """
        This method creates a new shell or python process.

        @param command: The command to be executed
        @param stdout: The stdout of the process
        @param stderr: The stderr of the process
        @param wait: Whether to wait for the process to finish
        """

        from .handler import \
            handler  # __Really ugly__ import to avoid circular dependency

        #
        @handler.subprocess_handler
        def __run(command, *args):
            """
            Simple alias function to avoid missuse of SIGTERMs and SIGINTS in multiple subprocess.
            """
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            command(*args)

        # assert self.__check_errors() # Perhaps, add this check function
        process = None
        if callable(command):
            LOGGER.debug(f"Creating process: {command} with args={args}")
            process = Process(
                target=__run, args=(command, *args), name=command.__name__
            )
            # process = Process(target=command, args=args, name=command.__name__)
            self.processes.append(process)
            process.start()
            if wait:
                LOGGER.debug(f"Waiting for process: {process} using _parent_conn")
                self._parent_conn.recv()
                LOGGER.debug(f"Process {process} is free to go, since all work is done")
        else:
            LOGGER.debug(
                f"Creating process: {command} with stdout={stdout} and stderr={stderr}"
            )
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
            self.processes.append(process)
            if wait:
                process.wait()

    def kill_processes(self):
        """
        This method kills all the processes.
        """
        if not self.processes:
            return
        while self.processes:
            process = self.processes.pop()
            self.kill_process(process)

    def kill_process(self, process):
        """
        This method kills a specific process.

        @param process: The process to be killed
        """
        LOGGER.debug(f"Killing process: {process}")
        # pid, status = os.waitpid(-1, os.WNOHANG)
        process.kill()
        if isinstance(process, Process):
            # Ensure is a child process
            if process._parent_pid == os.getpid():
                process.join()
        else:
            process.wait()


PROCESS = process()
