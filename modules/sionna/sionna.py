# import sionna.rt as RT
import os
import time

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
        import sionna.rt as RT  # TODO: Fix in-import (unregister the CUDA node before importing)

        self.buffer = IdealBuffer(
            1000
        )  # !< Buffer of the module (using size equal to 1000)
        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.scene = RT.load_scene(dir_path + "/beach_street.xml", merge_shapes=True)
        LOGGER.info(f"Loading scene {self.scene}")
        self.scene.frequency = 2.8e9
        self.solver = RT.PathSolver()
        """
        Set the transmitter and receiver arrays.
        """
        self.scene.tx_array = RT.PlanarArray(
            num_rows=1,
            num_cols=1,
            vertical_spacing=0.5,
            horizontal_spacing=0.5,
            pattern="iso",
            polarization="V",
        )

        self.scene.rx_array = RT.PlanarArray(
            num_rows=1,
            num_cols=1,
            vertical_spacing=0.5,
            horizontal_spacing=0.5,
            pattern="iso",
            polarization="V",
        )

        """
        Set and add the transmitter and receiver to the scene.
        """
        tx = RT.Transmitter(name="tx", position=[-195.4, 230.51, 81]) # Tx above a building
        self.scene.add(tx)
        rx = RT.Receiver(name="rx", position=[-208.75, 200.15, 1.02])
        self.scene.add(rx)

        # Make sure the transmitter and receiver are looking at each other
        tx.look_at(rx)  # Transmitter points towards receiver
        rx.look_at(tx)  # Receiver points towards transmitter

        LOGGER.debug(f"Finalizing Sionna Do Init")

    async def _execute_step(self):
        """
        This method executes the Sionna step.
        """
        LOGGER.info(f"Sionna Execute Step")
        self.scene.get("rx").position = np.array(
            self.convertMovementFromAirSimToSionna(self.buffer.get()[0]),
            dtype=np.float32,
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

        coefficients_real, coefficients_imag = np.array(paths.a)
        # Get the coefficients of the paths (rxAntennas, txAntennas, mpcs), since its only one
        # rx and tx, we can just take the first element. Since its a SISO, we can just take the first element
        # of the coefficients -> [mpcs]
        coefficients_real = coefficients_real[0, 0, 0, 0, :] 
        coefficients_imag = coefficients_imag[0, 0, 0, 0, :]
        '''
        The phase is the angle of the complex number, and the magnitude is the absolute value for 
        each MPC. The taus are the delays for each MPC.
        '''
        phase  = np.angle(coefficients_real + 1j * coefficients_imag)
        magnitude = np.abs(coefficients_real + 1j * coefficients_imag)
        taus = np.array(paths.tau)[0, 0, :]
        LOGGER.info(
            f"Phases: {phase}, Magnitudes: {magnitude}, Delays: {taus}"
        )
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
        assert phase_len == magnitude_len == taus_len, "Phase, magnitude and taus are not the same length"
        if magnitude_len < 1: # or phase_len < 1 or taus_len < 1
            # @TODO: Check whether these values can be deterministic when null values are found
            magnitude = [1e-11] # Really low gain
            phase = [0]
            taus = [1]
        
        id_objects = paths.objects.numpy()[:, 0, 0, :].T.tolist() # Rays objects list
        msg = {
            "magnitudes": magnitude.tolist(),
            "phases": phase.tolist(),
            "delays": taus.tolist(),
            "id_objects": id_objects,
        }
        await NATS.send(
            self.__class__.__name__,
            msg,
            "ns3",
        )

    def convertMovementFromAirSimToSionna(
        self,
        airsim_position: list,
        initial_pose_offset: list = [-208.75, 200.15, 1.02] # Central-park [23.34, -3.42, 137.23]
    ):
        """
        Converts the NED (x: North, y: East, z: Down) coordinates from AirSim
        into Y-forward, Z-up coordinates for Sionna.

        @param airsim_position: The position in AirSim coordinates
        @param initial_pose_offset: The offset between the AirSim and Sionna coordinates
        @return: The position in Sionna coordinates

        """
        return [
            initial_pose_offset[0] + airsim_position[0],
            initial_pose_offset[1] - airsim_position[1],
            initial_pose_offset[2] - airsim_position[2],
        ]
