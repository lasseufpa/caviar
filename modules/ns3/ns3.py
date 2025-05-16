import cmath
import os
import shutil
import signal
import time

from kernel.buffer import Buffer
from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS
from kernel.process import PROCESS
from utils import Interpolators, RaytracingGenerator


class ns3(module):
    RX_ANTENNA_ARCHITECTURE = [2, 2]
    TX_ANTENNA_ARCHITECTURE = [6, 6]

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
        self.interpolator = Interpolators()  # Class to handle the interpolation
        self.mixed_channels = []  # List of mixed channels (original and interpolated)
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
            config_command, wait=True, cwd=ns_3_path, stdout=None, stderr=None
        )
        LOGGER.debug(
            f"ns3 Config Command: {config_command}. Here, the process may take a while to finish, since it needs to build the ns-3"
        )
        build_command = ["./ns3", "build", "-j8"]  # Using 8 threads to build
        PROCESS.create_process(
            build_command, wait=True, cwd=ns_3_path, stdout=None, stderr=None
        )
        # @TODO: Check if the user err the password
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

        # Now, we start the internet container, using a **really ugly** bash script,
        # like the cave men... This is necessary, since we need to create the entire setup
        # according to the ns-3 logic. Nothing avoids you to use a docker-compose to perform
        # this step, it is just more simple to use a bash script here.

        PROCESS.create_process(  # First, create the container and install dependencies
            [
                "sudo",
                "bash",
                os.path.join(dir_path, "construct.sh"),
            ],
            wait=True,
            cwd=dir_path,
            # stdout=None,
            # stderr=None,
        )

        PROCESS.create_process(  # Second, start the route and interfaces of the container
            [
                "sudo",
                "bash",
                os.path.join(dir_path, "start.sh"),
            ],
            wait=True,
            cwd=dir_path,
            # stdout=None,
            # stderr=None,
        )

        # If enable-monitor is set, we need to create a route from the internet container
        # to the caviar.grafana container. We use a simple bash (like the cave men again)
        # to do this
        if NATS.is_monitor():
            PROCESS.create_process(
                [
                    "sudo",
                    "bash",
                    os.path.join(dir_path, "monitor.sh"),
                ],
                wait=True,
                cwd=dir_path,
                # stdout=None,
                # stderr=None,
            )

    async def _execute_step(self):
        """
        This method executes the ns3 step.

        First, attempt to perform the interpolation of the channel coefficients and delays.
        Attempts to maitain the buffer always with 100 messages.
        """
        '''
        buffer_len = self.buffer.__len__()
        channels_len = len(self.mixed_channels)
        print(f"Buffer length: {buffer_len}")
        if buffer_len < 2 and channels_len == 0:
            return
        elif buffer_len % 2 == 0:
            if channels_len < 100:
                print(f"Entering interpolation")
                """
                Each buffer item countains a list with the values:
                channel_coefficients, phases, delays, id_objects, and angles (zenith and azimuth).
                To perform the interpolation between N messages, we need to extract the lists
                and perform the interpolation.
                """
                N_TERMS = 100 - buffer_len # Number of terms to be added to the original buffer
                pre_processed_rt_data = RaytracingGenerator(
                    [self.buffer.get()[0][1]["sionna"] for _ in range(buffer_len)]  
                ).get_dataset()
                """
                The interpolated data is a dictionary where the keys are the index of the scenes.
                The values are the interpolated data, where each index is a list of MPCs. In each
                MPC, we have, respectively, a list of:
                - Magnitude
                - Zenith angle of arrival
                - Azimuth angle of arrival
                - Zenith angle of departure
                - Azimuth angle of departure
                - Phase
                - Delay
                """
                interpolated_scenes = self.interpolator.linear_n_factor_interp(pre_processed_rt_data, n_terms=N_TERMS)
                """
                Since we are working with lists, we need to convert the dictionary
                to a list of lists.
                """
                for i_scene in interpolated_scenes.keys():

                        if isinstance(interpolated_scenes[i_scene], dict):
                            interpolated_scenes[i_scene] = [interpolated_scenes[i_scene][rayIdx] for rayIdx in interpolated_scenes[i_scene].keys()]
                        self.mixed_channels.append(interpolated_scenes[i_scene])
                del pre_processed_rt_data, interpolated_scenes
        '''
        msg = self.buffer.get()[0][1]["sionna"]
        magnitude = msg["path_coef"]
        phase = msg["phase"]
        delays = msg["tau"]
        if True:
            """
            current_scene = self.mixed_channels.pop(0) # Get the most past scene
            '''
            Get each magnitude, phase and delay from the scene.
            '''
            magnitude = [mpc[0] for mpc in current_scene]
            phase = [mpc[5] for mpc in current_scene]
            delays = [mpc[6] for mpc in current_scene]
            del current_scene
            assert len(magnitude) == len(phase) == len(delays), "Magnitude, phase and delays should have the same length"
            """
            coefficients = [
                [[cmath.rect(magnitude[i], phase[i])]] for i in range(len(magnitude))
            ]
            """
            for i in range(len(magnitude)):
                coefficients.append(
                    [
                        [
                            complex(magnitude[i][j][k], phase[i][j][k])
                            for k in range(len(magnitude[i][j]))
                        ]
                        for j in range(len(magnitude[i]))
                    ]
                )
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
            # Write in the fifo file.
            Here its a block operation, since the ns-3 will read the file
            and will not continue until the file is read.
            """
            with open(os.path.join(self.ns3_path, "coefficients.fifo"), "w") as f:
                f.write(str(coefficients))
            with open(os.path.join(self.ns3_path, "delays.fifo"), "w") as f:
                f.write(str(delays))

    def __from_siso_to_mimo(self, phase: list, magnitude: list):
        """
        This method converts (estimates) the SISO H(f) coefficients to a _single port_ MIMO coefficients.
        sionna returns a list of phase and magnitude, where each index corresponds to a multipath component.
        ns-3 main code expects a list of MPCs, where each index is a list of MPCs for each RX antenna.
        For instance, if antennas (rx X tx) are 2x2, the coefficients should be:

        [
            [
                [H11, H12],
                [H21, H22]
            ],
            [
                [H31, H32],
                [H41, H42]
            ]
        ]

        - The first dimension corresponds to the number of multipath components.
        - The second dimension corresponds to the RX antennas.
        - The third dimension corresponds to the TX antennas.

        Where H11 is the coefficient for RX antenna 1 and TX antenna 1, and so on.
        Refer to https://arxiv.org/html/2504.21719v1#S2 Eq. 29. Using the same scheme of
        synthetic array (considering the distance between rx and tx >> distance between antenna elements):

        .. math::
            H_{array, n} = a_n* U^{rx}_A * (U^{tx}_A)^T,
        where n is the n-th MPC, a_n is the channel coefficient of the n-th MPC,
        U^{rx}_A is the rx array response vector and U^{tx}_A is the tx array response vector, according to:

        .. math::

        U^{rx}_A = [1, e^{-j \frac{2 \pi}{\lambda} d_{rx} *\hat{K})}, e^{-j \frac{2 \pi}{\lambda} d_{rx} *\hat{K})}, ...]
        U^{tx}_A = [1, e^{-j \frac{2 \pi}{\lambda} d_{tx} *\hat{K})}, e^{-j \frac{2 \pi}{\lambda} d_{tx} *\hat{K})}, ...]

        Where d_{rx} and d_{tx} are the distance between the antennas in the rx and tx arrays, respectively, and K is
        the wave vector of the derparture and arrival angles.
        """
        assert len(phase) == len(
            magnitude
        ), "Phase and magnitude should have the same length"
        coefficients = []
