import subprocess
import signal
import threading
import time
import sys
from pynats import NATSClient
import json


def signal_handler(sig, frame):
    global key
    print("Ctrl+C detected. Stopping the thread.")
    key = "w"
    abort_simulation()
    sys.exit(0)


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
                "3d/central_park/LinuxNoEditor/central_park/Binaries/Linux/central_park-Linux-DebugGame",
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
                "python",
                "examples/airsimTools/caviar_integration.py",
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
                "python",
                "examples/sionna/followPath.py",
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
        time.sleep(8)
        communications_thread.start()
    except Exception as e:
        print(f"Error: {str(e)}")

    def abort_simulation():
        print("The program was terminated manually!")
        time.sleep(1)
        airsim_simu.send_signal(signal.SIGTERM)
        time.sleep(1)
        airsim_simu.send_signal(signal.SIGTERM)
        time.sleep(1)
        airsim_simu.send_signal(signal.SIGTERM)
        time.sleep(1)
        nats_simu.send_signal(signal.SIGTERM)
        mobility_simu.send_signal(signal.SIGTERM)
        sionna_simu.send_signal(signal.SIGTERM)
        airsim_simu.wait()
        nats_simu.wait()
        mobility_simu.wait()
        sionna_simu.wait()
        print("------------------------------------------> END")
        sys.exit(0)

    with NATSClient() as natsclient:
        natsclient.connect()

        def simulation_check(msg):
            payload = json.loads(msg.payload.decode())
            isFinished = payload["isFinished"]
            if isFinished == "True":
                abort_simulation()
                sys.exit(0)

        natsclient.subscribe(subject="simulation.status", callback=simulation_check)
        natsclient.wait(count=1)
        while True:
            pass
            natsclient.wait(count=1)
