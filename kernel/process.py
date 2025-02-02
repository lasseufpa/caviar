import subprocess

from .logger import LOGGER


class process:
    """
    This class is responsible for processes management.
    """

    def __init__(self):
        """
        Constructor that initializes the Process object.
        """
        self.processes = []

    def create_process(self, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
        """
        This method creates a new process.

        @param command: The command to be executed
        @param stdout: The stdout of the process
        @param stderr: The stderr of the process
        """
        LOGGER.debug(
            f"Creating process: {command} with stdout={stdout} and stderr={stderr}"
        )
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
        self.processes.append(process)

    def kill_processes(self):
        """
        This method kills all the processes.
        """
        for process in self.processes:
            self.kill_process(process)

    def kill_process(self, process):
        """
        This method kills a specific process.

        @param process: The process to be killed
        """
        LOGGER.debug(f"Killing process: {process}")
        process.kill()
        process.wait()


PROCESS = process()
