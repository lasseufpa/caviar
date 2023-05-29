from execute_run import run
from pynats import NATSClient
import json

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


with NATSClient() as natsclient:
    natsclient.connect()

    def executeOneStep(msg):
        """Executes step on Sionna according to the current position in AirSim.

        Args:
            current_step (int): The current step index
        """
        payload = json.loads(msg.payload.decode())
        sionna_position = convertMovementFromAirSimToSionna(payload["position"])
        run(
            current_step=payload["timestamp"],
            new_x=sionna_position["x"],
            new_y=sionna_position["y"],
            new_z=sionna_position["z"],
        )
        natsclient.publish(subject="caviar.su.sionna.state", payload=b"Ready")
        natsclient.wait(count=total_ues)

    natsclient.subscribe(
        subject="caviar.ue.mobility.positions", callback=executeOneStep
    )

    natsclient.publish(subject="caviar.su.sionna.state", payload=b"Ready")
    natsclient.wait(count=total_ues)
