import cmath
import json
import os
import shutil
import signal
import time
from math import ceil

import aiofiles
import numpy as np
from scipy.constants import speed_of_light

from kernel.buffer import Buffer
from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS, asyncio
from kernel.process import PROCESS
from utils import Interpolators, RaytracingGenerator


class ns3(module):

    K = 55
    """
    Distortion factor for the interpolation.
    We assume that each position is saved every 55 ms.
    Therefore, the first channel is calculated at 0 ms and the last channel
    is calculated at 55 ms. The interpolation will be performed between these two
    channels, assuming an upper bound value K. If K is too high, the interpolation
    will create more channels than necessary. All these channels will be
    mapped in the rt/ns3/nr module, which expects one channel per 1 ms. So, if you increase
    the number of channels, each channel will be mapped to an incorrect ns-3 virtual time.
    For example, if K is larger than 55 (e.g., 110), each channel will represent a time of 0.5 ms,
    while ns-3 will interpret it as a 1 ms channel. This will cause a major desynchronization
    between the ns-3 and the Python simulation.

    @NOTE: Because ns-3 waits until a channel is consumed, even when using larger values of K,
    it should eventually synchronize itself with the Python simulation.
    """

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
        parent_dir_path = os.path.dirname(dir_path)
        ns_3_path = os.path.join(dir_path, "ns-3-dev")
        self.ns3_path = ns_3_path
        self.CONFIG = json.load(open(parent_dir_path + "/sionna/sionna.json"))
        assert self.CONFIG is not None, "sionna.json configuration file not found"
        self.RX_ANTENNA_ARCHITECTURE = [
            self.CONFIG["rx"]["rows"],
            self.CONFIG["rx"]["columns"],
        ]
        self.TX_ANTENNA_ARCHITECTURE = [
            self.CONFIG["tx"]["rows"],
            self.CONFIG["tx"]["columns"],
        ]
        """
        @TODO: These values of frequency and spacing are hardcoded and should be automatic set via
        sionna module 
        """
        self.tx_array_size = (
            self.TX_ANTENNA_ARCHITECTURE[0] * self.TX_ANTENNA_ARCHITECTURE[1]
        )
        self.rx_array_size = (
            self.RX_ANTENNA_ARCHITECTURE[0] * self.RX_ANTENNA_ARCHITECTURE[1]
        )
        self.is_siso = (
            True if self.tx_array_size == 1 and self.rx_array_size == 1 else False
        )
        self._frequency = self.CONFIG["scene_frequency"]
        self._wavelength = speed_of_light / self._frequency
        self._rx_rotation = None
        self._tx_rotation = None
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
        build_command = [
            "./ns3",
            "build",
            "-j8",
            "rt-tap-bridge",
        ]  # Using 8 threads to build
        PROCESS.create_process(
            build_command, wait=True, cwd=ns_3_path, stdout=None, stderr=None
        )
        run_command = [
            "./ns3",
            "run",
            "--enable-sudo",
            "rt-tap-bridge",
            "--",
            f"--ueRowNum={self.RX_ANTENNA_ARCHITECTURE[0]}",
            f"--ueColumnNum={self.RX_ANTENNA_ARCHITECTURE[1]}",
            f"--enbRowNum={self.TX_ANTENNA_ARCHITECTURE[0]}",
            f"--enbColumnNum={self.TX_ANTENNA_ARCHITECTURE[1]}",
            f"--equivalent={not self.is_siso}",
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

    async def _execute_step(self):

        """
        This method executes the ns3 step.
        First, attempt to perform the interpolation of the channel coefficients and delays.
        Attempts to maitain the inner-buffer always with 100 channels.
        """
        assert self.ns3_process is not None, "ns-3 process crashed for some reason"
        buffer_len = self.buffer.__len__()
        channels_len = len(self.mixed_channels)
        if buffer_len < 2 and channels_len == 0:
            return
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

        """
        Each buffer item countains a list with the values:
        magnitudes, phases, delays, id_objects, and angles (zenith and azimuth).
        To perform the interpolation between N messages, we need to extract the lists
        and perform the interpolation.

        @TODO: We should check how to generate a logic to perform the upsampling action

        """
        raw_data = [self.buffer.get()[0][1]["sionna"] for _ in range(2)]
        time = (raw_data[1]["timestamp"] - raw_data[0]["timestamp"]) / 1e6
        N_TERMS = (
            min(ceil(time), self.K * 2) if buffer_len < self.K / 4 else ceil(self.K)
        )
        """
        (
            min(ceil(time), self.K * 2) if buffer_len < self.K / 4 else ceil(self.K)
        )
        """
        assert N_TERMS > 0, "N_TERMS must be greater than 0"
        if self._rx_rotation is None and self._tx_rotation is None:
            self._rx_rotation = raw_data[0]["rx_rotation"]
            self._tx_rotation = raw_data[0]["tx_rotation"]
        pre_processed_rt_data = RaytracingGenerator(raw_data).get_dataset()
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
        interpolated_scenes = self.interpolator.linear_n_factor_interp(
            pre_processed_rt_data, n_terms=N_TERMS
        )
        """
        Since we are working with lists, we need to convert the dictionary
        to a list of lists.
        """
        for i_scene in interpolated_scenes.keys():
            if isinstance(interpolated_scenes[i_scene], dict):
                interpolated_scenes[i_scene] = [
                    interpolated_scenes[i_scene][rayIdx]
                    for rayIdx in interpolated_scenes[i_scene].keys()
                ]
            self.mixed_channels.append(interpolated_scenes[i_scene])
        del pre_processed_rt_data, interpolated_scenes

        while len(self.mixed_channels) > 0:
            """ """
            current_scene = self.mixed_channels.pop(0)  # Get the most past scene
            """
            Get each magnitude, phase and delay from the scene.
            """
            if self.is_siso:
                magnitude = [mpc[0] for mpc in current_scene]
                phase = [np.deg2rad(mpc[5]) for mpc in current_scene]
                h_mimo = [
                    [[cmath.rect(magnitude[i], phase[i])]]
                    for i in range(len(magnitude))
                ]
            else:
                a_real, a_imag = [
                    mpc[0] * np.cos(np.deg2rad(mpc[5])) for mpc in current_scene
                ], [mpc[0] * np.sin(np.deg2rad(mpc[5])) for mpc in current_scene]
                angles = {
                    "zenith_aoa": [np.deg2rad(mpc[1]) for mpc in current_scene],
                    "azimuth_aoa": [np.deg2rad(mpc[2]) for mpc in current_scene],
                    "zenith_aod": [np.deg2rad(mpc[3]) for mpc in current_scene],
                    "azimuth_aod": [np.deg2rad(mpc[4]) for mpc in current_scene],
                }
                h_mimo = self.__from_siso_to_mimo_drjit(
                    a_real=a_real, a_imag=a_imag, angles=angles
                )
            delays = [mpc[6] for mpc in current_scene]
            del current_scene
            with open(os.path.join(self.ns3_path, "coefficients.fifo"), "w") as f:
                f.write(str(h_mimo))
            with open(os.path.join(self.ns3_path, "delays.fifo"), "w") as f:
                f.write(str(delays))

    def __from_siso_to_mimo_drjit(self, a_real: list, a_imag: list, angles: dict):
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
                [H11, H12],
                [H21, H22]
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
        assert len(a_real) == len(a_imag), "Real and imaginary parts must match"

        a_complex = np.array(a_real) + 1j * np.array(a_imag)

        rx_pos = np.stack(
            (self._rx_rotation[0], self._rx_rotation[1], self._rx_rotation[2]), axis=-1
        )
        tx_pos = np.stack(
            (self._tx_rotation[0], self._tx_rotation[1], self._tx_rotation[2]), axis=-1
        )

        k_rx = np.stack(
            [
                np.sin(angles["zenith_aoa"]) * np.cos(angles["azimuth_aoa"]),
                np.sin(angles["zenith_aoa"]) * np.sin(angles["azimuth_aoa"]),
                np.cos(angles["zenith_aoa"]),
            ],
            axis=-1,
        )

        k_tx = np.stack(
            [
                np.sin(angles["zenith_aod"]) * np.cos(angles["azimuth_aod"]),
                np.sin(angles["zenith_aod"]) * np.sin(angles["azimuth_aod"]),
                np.cos(angles["zenith_aod"]),
            ],
            axis=-1,
        )
        factor = 2 * np.pi / self._wavelength
        phase_rx = factor * k_rx @ rx_pos.T
        phase_tx = factor * k_tx @ tx_pos.T

        U_rx = np.exp(1j * phase_rx)
        U_tx = np.exp(1j * phase_tx)
        H = a_complex[:, None, None] * U_rx[:, :, None] * U_tx[:, None, :]
        """
        Perform beamforming channel calculation (equivalent channel)
        """
        W_tx = np.exp(-1j * phase_tx)
        W_rx = np.exp(-1j * phase_rx)  # conjugate of the rx array response

        w_rx = W_rx.mean(axis=0)
        w_tx = W_tx.mean(axis=0)
        """
        Normalization
        """
        w_rx /= np.sqrt(len(w_rx))
        w_tx /= np.sqrt(len(w_tx))
        H_eff = (w_rx.conj().T @ H @ w_tx).tolist()
        # return H.tolist()
        return [[[c]] for c in H_eff]  # correct format for ns-3/nr/rt

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
