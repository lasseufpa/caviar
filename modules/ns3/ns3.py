import os
import shutil
import signal

from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS
from kernel.process import PROCESS


class ns3(module):
    def _do_init(self):
        """
        This method initializes all the necessary ns3 configuration.
        In this class, we will set up the ns3 environment and prepare it for execution.
        In this class, ns-3/nr is responsible by providing the 5G network simulation.
        The ns-3 will start the simulation and create a tap interface (tap0) in the host machine.
        Understand that this blueprint works in the real world (or something like this) and obviously:
        outside the ns-3 simulation.

        Because nats works in the python class (ns3) and ns-3 works in the C++ class, the communication
        will work using FIFO files, and it does not fit how ns-3 properly works, but it is the only way
        to make the message exchanging between the outside world and ns-3, without using any other type
        of communication (like sockets, etc).

        Because its a FIFO file, the python class will be the writer and the ns-3 will be the reader.
        And because of that, the simulation will only continue (calling again _execute_step) when the ns-3
        simulation consumes the message.
        """
        LOGGER.debug(f"ns3 Do Init")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ns_3_path = os.path.join(dir_path, "ns-3-dev")
        if not os.path.exists(ns_3_path):
            raise ValueError(
                "ns3 should be installed. Please do: git submodule update --init --recursive"
            )

        # Check if the modules are in the same dir of ns-3
        if os.path.exists(os.path.join(dir_path, "nr")) and os.path.exists(
            os.path.join(dir_path, "rt")
        ):
            shutil.move(
                os.path.join(dir_path, "nr"), os.path.join(ns_3_path, "contrib")
            )
            shutil.move(
                os.path.join(dir_path, "rt"), os.path.join(ns_3_path, "contrib")
            )
        # Check if its already installed in ns-3-dev
        elif os.path.exists(
            os.path.join(ns_3_path, "contrib", "nr")
        ) and os.path.exists(os.path.join(ns_3_path, "contrib", "rt")):
            pass
        else:
            raise ValueError(
                "Something went wrong with submodules. Please do: git submodule update --init --recursive"
            )

        # Before starting the simulation, we should create the fifo files. One for channel (coefficients),
        # second for delays. Clean it if already exists
        if os.path.exists(os.path.join(ns_3_path, "coefficients.fifo")):
            os.remove(os.path.join(ns_3_path, "coefficients.fifo"))
        if os.path.exists(os.path.join(ns_3_path, "delays.fifo")):
            os.remove(os.path.join(ns_3_path, "delays.fifo"))

        os.mkfifo(os.path.join(ns_3_path, "coefficients.fifo"))
        os.mkfifo(os.path.join(ns_3_path, "delays.fifo"))
        # os.mkfifo(os.path.join(ns_3_path, "position.fifo")) Ignore position, since rt module does not use it
        # to perform any mobility calculation

        config_command = [
            "./ns3",
            "configure",
            "--enable-examples",
            "--build-profile=optimized",
            "--enable-eigen",
        ]
        PROCESS.create_process(
            config_command, wait=True, cwd=ns_3_path, stdout=None, stderr=None
        )
        build_command = ["./ns3", "build", "-j8"]  # Using 8 threads to build
        PROCESS.create_process(
            build_command, wait=True, cwd=ns_3_path, stdout=None, stderr=None
        )
        run_command = [
            "./ns3",
            "run",
            "--enable-sudo",
            "rt-tap-bridge",  # "--positionFile=position.fifo", "--delayFile=delays.fifo", "--coefficientsFile=coefficients.fifo"
        ]

        def _preexec_fn():
            """
            A preexec function that sets the process group to the child process and
            sets the SIGCHLD signal to default.

            This is necessary, since tap-bridge uses the os.waitpid() and it expects
            the response from the child process. caviar ignores all sigchld signals, so
            the child process will not be able to reponse. Because of this, we need to
            set the process group to the child process, so it can receive the SIGCHLD
            signal by caviar and also set sigchild to default in this specific process.
            """
            os.setpgrp()
            signal.signal(signal.SIGCHLD, signal.SIG_DFL)

        PROCESS.create_process(
            run_command,
            wait=True,
            cwd=ns_3_path,
            stdout=None,
            stderr=None,
            preexec_fnction=_preexec_fn,
        )

    async def _execute_step(self):
        """
        This method executes the ns3 step.
        """
        pass
