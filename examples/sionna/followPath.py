from execute_run import run
from pynats import NATSClient
import json

total_ues = 1


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

        predicted_bit_rate_Gbps = run(
            current_step=payload["timestamp"],
            new_x=sionna_position["x"],
            new_y=sionna_position["y"],
            new_z=sionna_position["z"],
        )

        if type(predicted_bit_rate_Gbps) == type(None):
            predicted_bit_rate_Gbps = 0

        natsclient.publish(subject="communications.state", payload=b"Ready")
        natsclient.publish(
            subject="communications.throughput",
            payload=b'{"throughput":'
            + b'"'
            + str(predicted_bit_rate_Gbps).encode()
            + b'"'
            + b"}",
        )

    natsclient.subscribe(subject="3D.mobility.positions", callback=executeOneStep)

    natsclient.publish(subject="communications.state", payload=b"Ready")
    natsclient.publish(
        subject="communications.throughput", payload=b'{"throughput":"0"}'
    )
    natsclient.wait(count=total_ues)

    while True:
        pass
        natsclient.wait(count=total_ues)
