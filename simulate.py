import subprocess
import threading
import time


class runNatsServer(threading.Thread):
    def __init__(
        self,
    ):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runNatsServer")
        subprocess.run("nats-server", capture_output=True)


class runAirSim(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runAirSim")
        subprocess.run(
            "/home/joaoborges/Downloads/v2_central_parkUE4.27.2ExeLinux/LinuxNoEditor/central_park/Binaries/Linux/central_park-Linux-Shipping",
            capture_output=True,
        )


class runMobility(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runMobility")
        subprocess.run(
            [
                "/home/joaoborges/miniconda3/envs/tf/bin/python",
                "/home/joaoborges/codes/caviar/examples/airsimTools/caviar_integration.py",
            ],
            capture_output=True,
        )


class runSionna(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runSionna")
        subprocess.run(
            [
                "/home/joaoborges/miniconda3/envs/tf/bin/python",
                "/home/joaoborges/codes/caviar/examples/sionna/followPath.py",
            ],
            capture_output=True,
        )


if __name__ == "__main__":
    orchestrator_thread = runNatsServer()
    threeD_thread = runAirSim()
    mobility_thread = runMobility()
    communications_thread = runSionna()

    try:
        orchestrator_thread.start()
        threeD_thread.start()
        time.sleep(5)
        # mobility_thread.start()
        # communications_thread.start()
    except Exception as e:
        print(f"Error: {str(e)}")

    print("------------------------------------------> END")
