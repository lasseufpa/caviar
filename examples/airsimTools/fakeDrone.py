import time
from pynats import NATSClient


def reset():
    # fake_uav["position"] = [-110, 10, 100]  # start
    fake_uav["position"] = [-146, 82, 100]  # start
    # fake_uav["position"] = [-144.5, 79, -100]  # intersection
    # fake_uav["position"] = [-27, 146.5, -100] # upper limit


def move(step):
    print("Up")
    fake_uav["position"][0] = fake_uav["position"][0] + 1
    fake_uav["position"][1] = fake_uav["position"][1] + 0.4
    # if fake_uav["position"][0] > -144.5:
    #     print("Right")
    #     # Right
    #     fake_uav["position"][0] = fake_uav["position"][0] - 0.5
    #     fake_uav["position"][1] = fake_uav["position"][1] + 1
    # else:
    #     print("Up")
    #     fake_uav["position"][0] = fake_uav["position"][0] + 1
    #     fake_uav["position"][1] = fake_uav["position"][1] + 0.6
    ## Down
    # fake_uav["position"][0] = fake_uav["position"][0] - 1
    # fake_uav["position"][1] = fake_uav["position"][1] - 0.6
    # fake_uav["position"][2] = 100


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

    step_counter = 0

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

        fake_uav["move"](step=step_counter)
        step_counter = step_counter + 1
