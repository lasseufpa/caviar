import os
import signal
import time
import aiofiles
import shutil

from kernel.buffer import Buffer
from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS, asyncio
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

        # Before starting the simulation, we should create the fifo files.
        if os.path.exists(os.path.join(ns_3_path, "mobility.fifo")):
            os.remove(os.path.join(ns_3_path, "mobility.fifo"))

        os.mkfifo(os.path.join(ns_3_path, "mobility.fifo"))

        """
        Before starting the ns-3 simulation, we need to start the docker container
        that will be used to simulate the internet node. This is done using a bash script
        that will create the container and start the route and interfaces of the container.
        
        Now, we start the internet container, using a **really ugly** bash script,
        like the cave men... This is necessary, since we need to create the entire setup
        according to the ns-3 logic. Nothing avoids you to use a docker-compose to perform
        this step, it is just more simple to use a bash script here.
        """

        PROCESS.create_process(  # First, create the container and install dependencies
            [
                "sudo",
                "bash",
                os.path.join(dir_path, "construct.sh"),
            ],
            wait=True,
            cwd=dir_path,
            stdout=None,
            stderr=None,
        )
        PROCESS.create_process(  # Second, configure the route and interfaces of the container
            [
                "sudo",
                "bash",
                os.path.join(dir_path, "start.sh"),
            ],
            wait=True,
            cwd=dir_path,
            stdout=None,
            stderr=None,
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

        config_command = [
            "./ns3",
            "configure",
            "--enable-examples",
            "--build-profile=optimized",  # change optimized to debug in case some error happens;
            "--enable-eigen",
            "--enable-sudo",
        ]
        PROCESS.create_process(
            config_command, wait=True, cwd=ns_3_path, stdout=None, stderr=None
        )
        LOGGER.debug(
            f"ns3 Config Command: {config_command}. Here, the process may take a while to finish, since it needs to build the ns-3"
        )
        build_command = [
            "./ns3",
            "build",
            "-j8",
            "ntn-tap-bridge",
        ]  # Using 8 threads to build
        PROCESS.create_process(
            build_command, wait=True, cwd=ns_3_path, stdout=None, stderr=None
        )
        run_command = ["./ns3", "run", "--enable-sudo", "ntn-tap-bridge"]

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
        self.ns3_process = process
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

        # If enable-monitor is set, we need to create a route from the internet container
        # to the caviar.grafana container. We use a simple bash (like the cave men again)
        # to do this
        self.path_to_sinr_file = ""
        self.path_to_kpi_file = ""
        self.path_to_antenna_angles_file = ""
        self.path_to_mobility_sat = ""
        if NATS.is_monitor():
            PROCESS.create_process(
                [
                    "sudo",
                    "bash",
                    os.path.join(dir_path, "monitor.sh"),
                ],
                wait=True,
                cwd=dir_path,
                stdout=None,
                stderr=None,
            )
            self.path_to_sinr_file = os.path.join(ns_3_path, "sinr.txt")
            self.path_to_kpi_file = os.path.join(ns_3_path, "kpi.txt")
            self.path_to_antenna_angles_file = os.path.join(
                ns_3_path, "antenna_angles.txt"
            )
            self.path_to_mobility_sat = os.path.join(ns_3_path, "mobility.txt")
            """
            Since the event loop is not running yet, and loop.create_task is not available.
            We need to create a task that will run in the ns3 step (monitor parameters).
            The ns-3 main code overrides the oldest file which is already being monitored.
            To Prevent a bad behavior in the monitor class, we will remove the oldest to
            avoid monitor_file to read a file that goes to be overwritten.
            if os.path.exists(self.path_to_sinr_file):
                os.remove(self.path_to_sinr_file)
            """
            # if os.path.exists(self.path_to_kpi_file):
            # os.remove(self.path_to_kpi_file)

        self.is_already_monitored = False
        self.is_already_monitored_kpi = False
        self.is_already_monitored_antenna_angles = False
        self.is_already_monitored_mobility = False

        self.is_pinger_started = False

    def do_start_ping(self):
        """
        This method starts the ping to the internet node.
        It is used to check if the internet node is reachable.
        """
        LOGGER.debug(f"ns3 Do Start Ping")
        ping_command = ["ping", "-I", "tap0", "10.1.2.2"]
        ping_output_file = os.path.join("ping_output.txt")
        # Open file and keep it open for the ping process
        self.ping_output_file_handle = open(ping_output_file, "w")
        PROCESS.create_process(
            ping_command,
            stdout=self.ping_output_file_handle,
            stderr=self.ping_output_file_handle,
            process_name="ping_process",
        )

    async def _execute_step(self):

        """
        This method executes the ns3 step.
        First, attempt to perform the interpolation of the channel coefficients and delays.
        Attempts to maitain the inner-buffer always with 100 channels.
        """
        assert self.ns3_process is not None, "ns-3 process crashed for some reason"
        if self.is_already_monitored is False and os.path.exists(
            self.path_to_sinr_file
        ):
            asyncio.create_task(
                self._monitor_sinr(file_path=self.path_to_sinr_file, module_name="ns3")
            )
            self.is_already_monitored = True

        if self.is_already_monitored_kpi is False and os.path.exists(
            self.path_to_kpi_file
        ):
            asyncio.create_task(
                self._monitor_kpi(file_path=self.path_to_kpi_file, module_name="ns3")
            )
            self.is_already_monitored_kpi = True

        if self.is_already_monitored_antenna_angles is False and os.path.exists(
            self.path_to_antenna_angles_file
        ):
            asyncio.create_task(
                self._monitor_angles(
                    file_path=self.path_to_antenna_angles_file, module_name="ns3"
                )
            )
            self.is_already_monitored_antenna_angles = True

        if self.is_already_monitored_mobility is False and os.path.exists(
            self.path_to_mobility_sat
        ):
            asyncio.create_task(
                self._monitor_mobility_sat(
                    file_path=self.path_to_mobility_sat, module_name="ns3"
                )
            )
            self.is_already_monitored_mobility = True

        if not self.is_pinger_started:
            LOGGER.info("Starting ping to the internet node")
            self.do_start_ping()
            self.is_pinger_started = True
            asyncio.create_task(
                self._monitor_rtt(file_path="ping_output.txt", module_name="ns3")
            )

        airsim_data = self.buffer.get()[0][1]["airsim"]
        positions = f"{airsim_data['x-pos']} {airsim_data['y-pos']} {airsim_data['z-pos']}"  # {airsim_data["speed"]}
        with open(os.path.join(self.ns3_path, "mobility.fifo"), "w") as f:
            f.write(str(positions))

    async def _monitor_mobility_sat(self, file_path: str, module_name: str = "ns3"):
        module_name = self.__class__.__name__
        last_pos = 0
        async with aiofiles.open(file_path, "r") as file:
            while True:
                await file.seek(last_pos)
                lines = await file.readlines()
                if not lines:
                    await asyncio.sleep(0.05)
                    continue
                for line_content in lines:
                    parts = line_content.strip().split(":")
                    if len(parts) != 3:
                        continue
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                        z = float(parts[2])
                        LOGGER.debug(f"Monitoring Position: x={x}, y={y}, z={z}")
                        NATS.monitor_untracked_info(
                            info={"x": x, "y": y, "z": z},
                            module_name=module_name,
                        )
                    except ValueError:
                        continue
                last_pos = await file.tell()

    async def _monitor_rtt(self, file_path: str, module_name: str = "ns3"):
        module_name = self.__class__.__name__
        last_pos = 0
        async with aiofiles.open(file_path, "r") as file:
            while True:
                await file.seek(last_pos)
                lines = await file.readlines()
                if not lines:
                    await asyncio.sleep(0.05)
                    continue
                for line_content in lines:
                    parts = line_content.strip().split("=")
                    try:
                        rtt = float(parts[-1].replace(" ms", "").strip())
                        LOGGER.debug(f"Monitoring RTT: {rtt}")
                        NATS.monitor_untracked_info(
                            info={"rtt": rtt},
                            module_name=module_name,
                        )
                    except ValueError:
                        continue
                last_pos = await file.tell()

    async def _monitor_angles(self, file_path: str, module_name: str):
        module_name = self.__class__.__name__
        last_pos = 0
        async with aiofiles.open(file_path, "r") as file:
            while True:
                await file.seek(last_pos)
                lines = await file.readlines()
                if not lines:
                    await asyncio.sleep(0.05)
                    continue
                for line_content in lines:
                    parts = line_content.strip().split(":")
                    if len(parts) != 2:
                        continue
                    try:
                        alpha = float(parts[0])
                        beta = float(parts[1])
                        LOGGER.debug(f"Monitoring Angles: alpha={alpha}, beta={beta}")
                        NATS.monitor_untracked_info(
                            info={"alpha": alpha, "beta": beta},
                            module_name=module_name,
                        )
                    except ValueError:
                        continue
                last_pos = await file.tell()

    async def _monitor_sinr(self, file_path: str, module_name: str):
        module_name = self.__class__.__name__
        last_pos = 0
        async with aiofiles.open(file_path, "r") as file:
            while True:
                await file.seek(last_pos)
                lines = await file.readlines()
                if not lines:
                    await asyncio.sleep(0.05)  # Reduced sleep for faster polling
                    continue
                for line_content in lines:
                    parts = line_content.split()
                    if not parts:
                        continue
                    try:
                        value = float(parts[0])
                        # Optionally, only log on significant change
                        LOGGER.debug(f"Monitoring SINR: {value}")
                        NATS.monitor_untracked_info(
                            info={"sinr": value},
                            module_name=module_name,
                        )
                    except ValueError:
                        continue
                last_pos = await file.tell()
                # await asyncio.sleep(0.01)

    async def _monitor_kpi(self, file_path: str, module_name: str = "ns3"):
        """
        This method monitors the kpi file and sends the data to the monitor module.
        It is used to monitor the KPI file generated by ns-3.
        """
        last_pos = 0
        async with aiofiles.open(file_path, "r") as file:
            while True:
                await file.seek(last_pos)
                lines = await file.readlines()
                if not lines:
                    await asyncio.sleep(0.05)  # Reduced sleep for faster polling
                    continue
                for line_content in lines:
                    parts = line_content.split()
                    if not parts:
                        continue
                    try:
                        value = float(parts[0])
                        NATS.monitor_untracked_info(
                            info={"throughput": value},
                            module_name=module_name,
                        )
                    except ValueError:
                        continue
                last_pos = await file.tell()
