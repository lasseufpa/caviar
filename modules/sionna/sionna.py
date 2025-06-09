# import sionna.rt as RT
import os
import time
import json
import numpy as np

from kernel.idealBuffer import IdealBuffer
from kernel.logger import LOGGER
from kernel.module import module
from kernel.nats import NATS


class sionna(module):
    """
    The Sionna module is the class that handles all the Sionna setup
    """

    def _do_init(self):
        """
        This method initializes all the necessary Sionna configuration.
        """
        import sionna.rt as RT

        self.buffer = IdealBuffer(
            1000
        )  # !< Buffer of the module (using size equal to 1000)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # Read json with the configurations
        config = json.load(open(dir_path + "/sionna.json", "r"))
        self.scene = RT.load_scene(dir_path + "/beach_street.xml", merge_shapes=True)
        LOGGER.info(f"Loading scene {self.scene}")
        self.scene.frequency = config["scene_frequency"]  # 2.8e9
        self.solver = RT.PathSolver()
        """
        Set the transmitter and receiver arrays.
        """
        self.scene.tx_array = RT.PlanarArray(
            num_rows=1,
            num_cols=1,
            # vertical_spacing=0.5,
            # horizontal_spacing=0.5,
            pattern=config["tx"]["pattern"],
            polarization="V",
        )

        self.scene.rx_array = RT.PlanarArray(
            num_rows=1,
            num_cols=1,
            # vertical_spacing=0.5,
            # horizontal_spacing=0.5,
            pattern=config["rx"]["pattern"],
            polarization="V",
        )
        """
        Set and add the transmitter and receiver to the scene.
        """
        tx = RT.Transmitter(
            name="tx", position=config["tx"]["position"]  # [-195.4, 230.51, 81]
        )  # Tx above a building
        self.scene.add(tx)
        rx = RT.Receiver(
            name="rx", position=config["rx"]["position"]
        )  # [-208.75, 200.15, 1.02]
        self.scene.add(rx)

        # Make sure the transmitter and receiver are looking at each other
        # tx.look_at(rx)  # Transmitter points towards receiver
        rx.look_at(tx)  # Receiver points towards transmitter
        """
        Get the rotated (relative) positions of the antennas in the tx array, since its fixed
        in a specific position.
        """
        self._tx_rotation = self._rotate(
            num_cols=config["tx"]["columns"],
            num_rows=config["tx"]["rows"],
            d_v=config["tx"]["vcertical_antenna_spacing"],
            d_h=config["tx"]["horizontal_antenna_spacing"],
            orientation=np.array(tx.orientation),
        )
        self._rx_rotation = self._rotate(
            num_cols=config["rx"]["columns"],
            num_rows=config["rx"]["rows"],
            d_v=config["rx"]["vcertical_antenna_spacing"],
            d_h=config["rx"]["horizontal_antenna_spacing"],
            orientation=np.array(rx.orientation),
        )
        LOGGER.debug(f"Tx rotation: {self._tx_rotation}")
        LOGGER.debug(f"Rx rotation: {self._rx_rotation}")
        LOGGER.debug(f"Finalizing Sionna Do Init")

    async def _execute_step(self):
        """
        This method executes the Sionna step.
        """
        LOGGER.debug(f"Sionna Execute Step")
        element = self.buffer.get()
        if element is None:
            LOGGER.debug("No element in buffer, skipping Sionna step")
            return
        pose = element[0][:3]
        self.scene.get("rx").position = self.convertMovementFromAirSimToSionna(pose)
        roll, pitch, yaw = (element[0][3], element[0][4], element[0][5])
        self._rx_rotation = self._rotate(
            num_cols=2,
            num_rows=2,
            d_v=0.5,
            d_h=0.5,
            orientation=[roll, pitch, yaw],
        )
        start = time.time_ns()
        paths = self.solver(
            scene=self.scene,
            max_depth=5,
            los=True,
            specular_reflection=True,
            diffuse_reflection=True,
            refraction=True,
            synthetic_array=True,
            seed=41,
        )
        end = time.time_ns()
        LOGGER.debug(f"Sionna step took {end - start} ns ({(end - start) / 1e6} ms)")

        """
        Since the simulation is being made assuming a SISO communication, we need to
        save the angles to be able to calculate (estimate) the channel coefficients for a 
        MIMO communication afterwards.
        """
        phi_r = np.array(
            paths.phi_r[0, 0, :]
        ).tolist()  # All MPCs Azimuth angle of arrival
        phi_t = np.array(
            paths.phi_t[0, 0, :]
        ).tolist()  # All MPCs Azimuth angle of departure
        theta_r = np.array(
            paths.theta_r[0, 0, :]
        ).tolist()  # All MPCs  Zenith angle of arrival
        theta_t = np.array(
            paths.theta_t[0, 0, :]
        ).tolist()  # All MPCs  Zenith angle of departure

        coefficients_real, coefficients_imag = np.array(paths.a)
        # Get the coefficients of the paths (rxAntennas, txAntennas, mpcs), since its only one
        # rx and tx, we can just take the first element. Since its a SISO, we can just take the first element
        # of the coefficients -> [mpcs]
        coefficients_real = coefficients_real[0, 0, 0, 0, :]
        coefficients_imag = coefficients_imag[0, 0, 0, 0, :]
        """
        The phase is the angle of the complex number, and the magnitude is the absolute value for 
        each MPC. The taus are the delays for each MPC.
        """
        phase = np.angle(
            coefficients_real + 1j * coefficients_imag
        ).tolist()  # in radians
        magnitude = np.abs(coefficients_real + 1j * coefficients_imag).tolist()
        taus = np.array(paths.tau)[0, 0, :].tolist()  # All MPCs delays
        id_objects = paths.objects.numpy()[:, 0, 0, :].T.tolist()  # MPCs objects list
        LOGGER.debug(f"Phases: {phase}, Magnitudes: {magnitude}, Delays: {taus}")
        """
        When no paths are found, the coefficients are empty. 
        However, in ns-3/nr, it always expects a channel even if the gain is 
        really low.
        So we need to add a dummy path with a minor gain to prevent 
        ns-3/nr from crashing.
        """
        phase_len = len(phase)
        magnitude_len = len(magnitude)
        taus_len = len(taus)
        assert (
            phase_len == magnitude_len == taus_len
        ), "Phase, magnitude and taus are not the same length"
        if magnitude_len < 1:  # or phase_len < 1 or taus_len < 1
            LOGGER.info("No paths, sending really low gain MPCs")
            # @TODO: Check whether these values can be deterministic when null values are found
            magnitude = [1e-11]  # Really low gain
            phase = [0]
            taus = [1]
            theta_r = [0]
            theta_t = [0]
            phi_r = [0]
            phi_t = [0]
            id_objects = [0]

        del paths
        msg = {
            "path_coef": magnitude,
            "phase": phase,
            "tau": taus,
            "id_objects": id_objects,
            "theta_t": theta_t,
            "theta_r": theta_r,
            "phi_t": phi_t,
            "phi_r": phi_r,
            "rx_rotation": self._rx_rotation,
            "tx_rotation": self._tx_rotation,
        }
        await NATS.send(
            self.__class__.__name__,
            msg,
            "ns3",
        )

    def convertMovementFromAirSimToSionna(
        self,
        airsim_position: list,
        initial_pose_offset: list = [
            -208.75,
            200.15,
            1.02,
        ],  # Central-park [23.34, -3.42, 137.23]
    ):
        """
        Converts the NED (x: North, y: East, z: Down) coordinates from AirSim
        into Y-forward, Z-up coordinates for Sionna.

        @param airsim_position: The position in AirSim coordinates
        @param initial_pose_offset: The offset between the AirSim and Sionna coordinates
        @return: The position in Sionna coordinates

        """
        pos = np.array(airsim_position, dtype=np.float32)
        offset = np.array(initial_pose_offset, dtype=np.float32)
        return offset + pos * np.array([1, -1, -1], dtype=np.float32)

    def _rotate(self, orientation, d_v=0.5, d_h=0.5, num_rows=1, num_cols=1):
        r"""
        @SIONNA_FUNCTION

        Computes the relative positions of all antennas rotated according
        to the ``orientation``

        Dual-polarized antennas are counted as a single antenna and share the
        same position.

        Positions are computed by scaling the normalized positions of antennas
        by the ``wavelength`` and rotating by ``orientation``.

        :param wavelength: Wavelength [m]

        :param orientation: Orientation [rad] specified through three angles
            corresponding to a 3D rotation as defined in :eq:`rotation`

        :returns: Rotated relative antenna positions :math:`(x,y,z)` [m]
        """
        a = orientation[0]  # angles.x
        b = orientation[1]  # angles.y
        c = orientation[2]  # angles.z
        sin_a, cos_a = np.sin(a), np.cos(a)  # dr.sincos(a)
        sin_b, cos_b = np.sin(b), np.cos(b)  # dr.sincos(b)
        sin_c, cos_c = np.sin(c), np.cos(c)  # dr.sincos(c)

        r_11 = cos_a * cos_b
        r_12 = cos_a * sin_b * sin_c - sin_a * cos_c
        r_13 = cos_a * sin_b * cos_c + sin_a * sin_c

        r_21 = sin_a * cos_b
        r_22 = sin_a * sin_b * sin_c + cos_a * cos_c
        r_23 = sin_a * sin_b * cos_c - cos_a * sin_c

        r_31 = -sin_b
        r_32 = cos_b * sin_c
        r_33 = cos_b * cos_c

        rot_mat = np.array(
            [[r_11, r_12, r_13], [r_21, r_22, r_23], [r_31, r_32, r_33]],
            dtype=np.float32,
        ).squeeze()

        array_size = num_rows * num_cols
        normalized_positions = np.zeros((3, array_size), dtype=np.float32)

        for i in range(num_rows):
            for j in range(num_cols):
                # Index of the antenna
                ind = i + j * num_rows
                # Set Y-Z positions
                # An offset is added to center the panel around the origin
                normalized_positions[1, ind] = j * d_h - (num_cols - 1) * d_h / 2  # y
                normalized_positions[2, ind] = -i * d_v + (num_rows - 1) * d_v / 2  # z
        # rot_mat = np.array(self.rot_matrix(orientation), dtype=np.float32).squeeze()
        p = normalized_positions * self.scene.wavelength  # shape (3, N)
        rot_p = rot_mat @ p
        return rot_p.tolist()
