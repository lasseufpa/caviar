import subprocess
import signal
import threading
from getch import getch
import time
from pynats import NATSClient
import json

key = "a"

def verifyKey():
    global key
    lock = threading.Lock()
    while True:
        with lock:
            pass
            # print("Thread Working...")
            # key = input("Press 'w' to close")

def signal_handler(sig, frame):
    global key
    print("Ctrl+C detected. Stopping the thread.")
    key = "w"
    time.sleep(10)
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

class runNatsServer(threading.Thread):
    def __init__(
        self,
    ):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runNatsServer")
        global nats_simu
        nats_simu = subprocess.Popen("nats-server")


class runAirSim(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runAirSim")
        global airsim_simu
        airsim_simu = subprocess.Popen(
            [
                "/home/fhb/Downloads/v4_central_parkUE4.27.2ExeLinux/LinuxNoEditor/central_park/Binaries/Linux/central_park-Linux-DebugGame",
                "-WINDOWED",
                "-ResX=640",
                "-ResY=480",
            ]
        )


class runMobility(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runMobility")
        global mobility_simu
        mobility_simu = subprocess.Popen(
            [
                "/home/fhb/miniconda3/envs/caviar_env/bin/python",
                "/home/fhb/git/caviar/examples/airsimTools/caviar_integration.py",
            ]
        )


class runSionna(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runSionna")
        global sionna_simu
        sionna_simu = subprocess.Popen(
            [
                "/home/fhb/miniconda3/envs/caviar_env/bin/python",
                "/home/fhb/git/caviar/examples/sionna/followPath.py",
            ]
        )


if __name__ == "__main__":
    orchestrator_thread = runNatsServer()
    threeD_thread = runAirSim()
    mobility_thread = runMobility()
    communications_thread = runSionna()

    try:
        orch_return = orchestrator_thread.start()
        threeD_thread.start()
        time.sleep(2)
        mobility_thread.start()
        time.sleep(2)
        communications_thread.start()
        threading.Thread(target = verifyKey).start()
    except Exception as e:
        print(f"Error: {str(e)}")

    # while True:
    #     res = input("Press 'w' to close")
    #     if res == "w":
    #         print("The program was terminated manually!")
    #         time.sleep(5)
    #         airsim_simu.send_signal(signal.SIGTERM)
    #         time.sleep(1)
    #         airsim_simu.send_signal(signal.SIGTERM)
    #         time.sleep(1)
    #         airsim_simu.send_signal(signal.SIGTERM)
    #         time.sleep(2)
    #         nats_simu.send_signal(signal.SIGTERM)
    #         mobility_simu.send_signal(signal.SIGTERM)
    #         sionna_simu.send_signal(signal.SIGTERM)
    #         print("------------------------------------------> END")
    #         break

    with NATSClient() as natsclient:
        natsclient.connect()

        def simulation_check(msg):
            """Executes step on Sionna according to the current position in AirSim.

            Args:
                current_step (int): The current step index
            """
            payload = json.loads(msg.payload.decode())
            isFinished = payload["isFinished"]
            if key == "w" or isFinished == "True":
                print("The program was terminated manually!")
                time.sleep(5)
                airsim_simu.send_signal(signal.SIGTERM)
                time.sleep(1)
                airsim_simu.send_signal(signal.SIGTERM)
                time.sleep(1)
                airsim_simu.send_signal(signal.SIGTERM)
                time.sleep(2)
                nats_simu.send_signal(signal.SIGTERM)
                mobility_simu.send_signal(signal.SIGTERM)
                sionna_simu.send_signal(signal.SIGTERM)
                print("------------------------------------------> END")
                exit(0)
            # natsclient.wait(count=1)
        natsclient.subscribe(
            subject="simulation.status", callback=simulation_check
        )
        natsclient.wait(count=1)
        while True:
            pass
            natsclient.wait(count=1)
        
