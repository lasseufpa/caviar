import os
import shutil
import signal
import time

from kernel.buffer import Buffer
from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS
from kernel.process import PROCESS


class ns3(module):
    def _do_init(self):
        """
        This method initializes all the necessary ns3 configuration.
        In this class, we will set up the ns3 environment and prepare it for execution.
        ns-3/nr is responsible by providing the 5G network simulation.
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

        @NOTE: The first run may take a while, because it needs to build the ns-3 simulation.
        """
        LOGGER.debug(f"ns3 Do Init")
        self.buffer = Buffer(100000)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ns_3_path = os.path.join(dir_path, "ns-3-dev")
        self.ns3_path = ns_3_path
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
            "--enable-sudo",
        ]
        PROCESS.create_process(
            config_command, wait=True, cwd=ns_3_path  # , stdout=None, stderr=None
        )
        LOGGER.debug(
            f"ns3 Config Command: {config_command}. Here, the process may take a while to finish, since it needs to build the ns-3"
        )
        build_command = ["./ns3", "build", "-j8"]  # Using 8 threads to build
        PROCESS.create_process(
            build_command, wait=True, cwd=ns_3_path  # , stdout=None, stderr=None
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
            @TODO: Check how to deal when ns-3 crashes.
            """
            # os.setpgrp()
            signal.signal(signal.SIGCHLD, signal.SIG_DFL)

        LOGGER.debug(f"ns3 Run Command: {run_command}")
        PROCESS.create_process(
            run_command,
            # wait=True, # This blocks the simulation
            cwd=ns_3_path,
            preexec_fnction=_preexec_fn,
            stdout=None,
            stderr=None,
            stdin=None,
            process_name="ns3_run",
        )

        # Necessary, since ns-3 requires the passwd and if we do not wait,
        # it will not be able to read the input. Here, we assume tap0 is the name
        # of the tap interface created by ns-3.
        process = PROCESS.get_process_by_name("ns3_run")
        while not os.path.exists("/sys/class/net/tap0"):
            if process.poll() is not None:
                raise ValueError(
                    "ns-3 crashed. Please check if something its wrong with installation, or the code"
                )
            time.sleep(0.5)  # Wait for the tap0 to be created
            pass
        # Here, we assume the tap0 is already present in the system
        # (you can check using ifconfig or ip a). Now, we define the
        # route to the internet node, through the ns-3 simulation:
        # sudo ip route add 10.1.2.0/24 via 10.1.1.1 dev tap0
        route_command = [
            "sudo",
            "ip",
            "route",
            "add",
            "10.1.2.0/24",
            "via",
            "10.1.1.1",
            "dev",
            "tap0",
        ]
        PROCESS.create_process(route_command, wait=True)  # , stderr=None, stdout=None

    async def _execute_step(self):
        """
        This method executes the ns3 step.
        """
        LOGGER.debug(f"ns3 Execute Step")
        message = self.buffer.get()[0]
        coefficients = message[1]["sionna"]["coefficients"]
        LOGGER.debug("Coefficients: %s", coefficients)
        coefficients = [
            [
                [complex(entry["real"], entry["imag"]) for entry in mpc_list]
                for mpc_list in tx_list
            ]
            for tx_list in coefficients
        ]
        coefficients = [
            [
                [coefficients[x][y][z] for y in range(len(coefficients[0]))]
                for x in range(len(coefficients))
            ]
            for z in range(len(coefficients[0][0]))
        ]
        delays = message[1]["sionna"]["delays"]
        """
        # Write in the fifo file.
        Here its a block operation, since the ns-3 will read the file
        and will not continue until the file is read.
        """
        with open(os.path.join(self.ns3_path, "coefficients.fifo"), "w") as f:
            f.write(str(coefficients))
        with open(os.path.join(self.ns3_path, "delays.fifo"), "w") as f:
            f.write(str(delays))
