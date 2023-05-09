import time
from pynats import NATSClient


def reset():
    fake_uav["position"] = [0, 0, 0]


def move():
    fake_uav["position"] = [pos + 1 for pos in fake_uav["position"]]


fake_uav = {"position": [0, 0, 0], "reset": reset, "move": move}


with NATSClient() as natsclient:
    #  Socket to talk to server
    natsclient.connect()

    def callback(msg):
        print(f"Received a message with subject {msg.subject}: {msg}")

    natsclient.subscribe(subject="caviar.su.sionna.state", callback=callback)

    print("Episode: " + str("fake_uav"))

    landed = False
    takeoff_complete = False

    # Reset the airsim simulation
    fake_uav["reset"]()

    # takeoff and start the UAV trajectory
    fake_uav["move"]()

    while True:
        time.sleep(1)

        # Get an write information about each UAV in the configuration file (caviar_config.py)
        uav_pose = fake_uav["position"]

        print("Sending request …")

        natsclient.publish(
            subject="caviar.ue.mobility.positions",
            payload=b'{"UE_type":"UAV","UE_Id":'
            + b'"'
            + str("uav1").encode()
            + b'"'
            + b',"timestamp":'
            + b'"'
            + str(time.time()).encode()
            + b'"'
            + b',"position": {"x":'
            + str(uav_pose[0]).encode()
            + b',"y":'
            + str(uav_pose[1]).encode()
            + b',"z":'
            + str(uav_pose[2]).encode()
            + b"}}",
        )
