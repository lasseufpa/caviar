from execute_run import run
from pynats import NATSClient
import json

total_ues = 1  # + len(caviar_config.ue_objects)

with NATSClient() as natsclient:
    natsclient.connect()

    def executeOneStep(msg):
        """Executes step on Sionna according to the current position in AirSim.

        Args:
            current_step (int): The current step index
        """
        payload = json.loads(msg.payload.decode())
        run(
            current_step=payload["timestamp"],
            new_x=payload["position"]["x"],
            new_y=payload["position"]["y"],
            new_z=payload["position"]["z"],
        )
        natsclient.wait(count=total_ues)

    natsclient.subscribe(
        subject="caviar.ue.mobility.positions", callback=executeOneStep
    )

    natsclient.wait(count=total_ues)
