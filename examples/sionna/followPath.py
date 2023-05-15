# from examples.sionna.execute_run import run
from execute_run import run
from pynats import NATSClient
import json
import numpy as np

with NATSClient() as natsclient:
    total_ues = 1  # + len(caviar_config.ue_objects)

    def convertMovementFromAirSimToSionna(airsim_position):
        """Converts the NED (x: North, y: East, z: Down) coordinates from AirSim
        into Y-forward, Z-up coordinates for Sionna.

        Args:
            airsim_position (dict): A dictionary containing the NED
                                    (x: North, y: East, z: Down)
                                    position from AirSim

        Returns:
            dict: A dictionary containing the Y-forward, Z-up coordinates for Sionna
        """
        return {
            "x": airsim_position["x"],
            "y": -airsim_position["y"],
            "z": -airsim_position["z"],
        }

    def executeOneStep(msg):
        """Executes step on Sionna according to the current position in AirSim.

        Args:
            current_step (int): The current step index
        """
        payload = json.loads(msg.payload.decode())
        sionna_position = convertMovementFromAirSimToSionna(payload["position"])
        (
            path_coefficients,
            path_delays,
            rx_airsim_position,
            rx_starting_position,
            rx_current_position,
            mimoChannel,
            equivalentChannel,
            equivalentChannelMagnitude,
            best_ray,
        ) = run(
            current_step=payload["timestamp"],
            new_x=sionna_position["x"],
            new_y=sionna_position["y"],
            new_z=sionna_position["z"],
        )
        natsclient.publish(
            subject="caviar.comm.rxpositionandbestray",
            payload=b'{"best_ray":' + b'"' + str(best_ray).encode() + b'"' + b"}",
        )
        # natsclient.publish(
        #     subject="caviar.comm.rxpositionandbestray",
        #     payload=b'{"best_ray":'
        #     + b'"'
        #     + str(best_ray).encode()
        #     + b'"'
        #     + b',"rx_current_position": {"x":'
        #     + str(rx_current_position[0]).encode()
        #     + b',"y":'
        #     + str(rx_current_position[1]).encode()
        #     + b',"z":'
        #     + str(rx_current_position[2]).encode()
        #     + b"}}",
        # )

    def sionnaStart():
        natsclient.connect()

        natsclient.subscribe(
            subject="caviar.ue.mobility.positions", callback=executeOneStep
        )

        natsclient.wait(count=total_ues)

    def sionnaStop():
        natsclient.close()

    natsclient.publish(
        subject="caviar.comm.rxpositionandbestray",
        payload=b'{"best_ray":"1"}',
    )
    # sionnaStart()
