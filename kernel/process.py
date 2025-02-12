import os
import signal
import subprocess
from multiprocessing import Lock, Manager, Pipe, Process, Queue, active_children

from .logger import LOGGER


class process(Process):
    """
    This class is responsible for processes management.

    @TODO: Check if it is necessary to be a subclass of Process. Because this class is not being used as a _Process_ subclass.
    We are using the _process_ module to `create` and `manage` processes.
    """

    QUEUE = Queue()
    LOCK = Lock()
    MANAGER = Manager()

    def __init__(self, *args, **kwargs):
        """
        Constructor that initializes the Process manager object.
        """
        # super().__init__(*args, **kwargs)
        self._parent_conn, self._child_conn = Pipe()
        self.processes = []

    def create_process(
        self,
        command,
        *args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        wait=False,
        process_name="",
    ):
        """
        This method creates a new shell or python process.

        @param command: The command to be executed
        @param stdout: The stdout of the process
        @param stderr: The stderr of the process
        @param wait: Whether to wait for the process to finish
        """

        from .handler import (
            handler,
        )  # __Really ugly__ import to avoid circular dependency

        #
        @handler.subprocess_handler
        def __run(command, *args):
            """
            Simple alias function to avoid missuse of SIGTERMs and SIGINTS in multiple subprocess.
            """
            LOGGER.debug(f"Subprocess ___{os.getpid()}___ created")
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            command(*args)

        # assert self.__check_errors() # Perhaps, add this check function
        process = None
        if callable(command):
            LOGGER.debug(f"Creating process: {command} with args={args}")
            if not process_name:
                process_name = command.__name__
            process = Process(target=__run, args=(command, *args), name=process_name)
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
            self.__kill_process(process)

    def __kill_process(self, process):
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

    def __get_process_by_name(self, name):
        """
        This method retrieves the (sub)process given a name

        @param name: The name of the process
        """
        for process in active_children():
            if process.name.lower() == name.lower():
                LOGGER.debug(f"Accessing (sub)process {process}")
                return process

    def check_state(self):
        """
        This method checks the state of the availability to execute steps in the given module (subprocess).
        It should be called ONLY in scheduler class
        """
        all_available_modules = []
        while not self.QUEUE.empty():
            LOGGER.debug("Checking state...")
            module_state = self.QUEUE.get()
            LOGGER.debug(f"Module state: {module_state}")
            if module_state[1]:
                all_available_modules.append(module_state[0])
        return all_available_modules


PROCESS = process()
