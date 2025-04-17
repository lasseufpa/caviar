# import sionna.rt as RT
import os
import time

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

        self.scene = RT.load_scene(dir_path + "/central_park.xml", merge_shapes=True)
        LOGGER.debug(f"Loading scene {self.scene}")
        self.scene.frequency = 28e9
        self.solver = RT.PathSolver()
        """
        Set the transmitter and receiver arrays.
        """
        self.scene.tx_array = RT.PlanarArray(
            num_rows=8,
            num_cols=8,
            vertical_spacing=0.5,
            horizontal_spacing=0.5,
            pattern="iso",
            polarization="V",
        )

        self.scene.rx_array = RT.PlanarArray(
            num_rows=2,
            num_cols=2,
            vertical_spacing=0.5,
            horizontal_spacing=0.5,
            pattern="iso",
            polarization="V",
        )

        """
        Set and add the transmitter and receiver to the scene.
        """
        tx = RT.Transmitter(name="tx", position=[-154, 64, 120])
        self.scene.add(tx)
        rx = RT.Receiver(name="rx", position=[23.69, -3.351, 139])
        self.scene.add(rx)

        # Make sure the transmitter and receiver are looking at each other
        tx.look_at(rx)  # Transmitter points towards receiver
        rx.look_at(tx)  # Receiver points towards transmitter

        LOGGER.debug(f"Finalizing Sionna Do Init")

    async def _execute_step(self):
        """
        This method executes the Sionna step.
        """
        LOGGER.debug(f"Sionna Execute Step")
        self.scene.get("rx").position = self.convertMovementFromAirSimToSionna(
            self.buffer.get()[0]
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
        LOGGER.info(f"Sionna step took {end - start} ns ({(end - start) / 1e6} ms)")
        """
        await NATS.send(
            self.__class__.__name__,
            {
                "paths": paths,
                "rx_pos": self.scene.get("rx").position,
                "tx_pos": self.scene.get("tx").position,
            },
            "airsim",
        )
        """

    def convertMovementFromAirSimToSionna(
        self,
        airsim_position: list,
        initial_pose_offset: list = [23.34, -3.42, 137.23],  # [14, -28, 8.4]
    ):
        """
        Converts the NED (x: North, y: East, z: Down) coordinates from AirSim
        into Y-forward, Z-up coordinates for Sionna.

        @param airsim_position: The position in AirSim coordinates
        @return: The position in Sionna coordinates

        """
        return [
            initial_pose_offset[0] + airsim_position[0],
            initial_pose_offset[1] - airsim_position[1],
            initial_pose_offset[2] - airsim_position[2],
        ]
