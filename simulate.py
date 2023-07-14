import subprocess
import signal
import threading
import time


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
        airsim_simu = subprocess.Popen([
            "/home/fhb/Downloads/central_park/central_park/Binaries/Linux/central_park-Linux-Shipping", "-WINDOWED", "-ResX=640", "-ResY=480"]
        )


class runMobility(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runMobility")
        global mobility_simu
        mobility_simu = subprocess.Popen(
            [
                "/home/fhb/miniconda3/envs/tf/bin/python",
                "/home/fhb/git/caviar/examples/airsimTools/caviar_integration.py"]
        )


class runSionna(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runSionna")
        global sionna_simu
        sionna_simu = subprocess.Popen(
            [
                "/home/fhb/miniconda3/envs/tf/bin/python",
                "/home/fhb/git/caviar/examples/sionna/followPath.py"
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
    except Exception as e:
        print(f"Error: {str(e)}")
    
    while True:
        res = input("Press 'w' to close")
        if res == "w":
            print("The Program is terminated manually!")
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
            print(f'orch_return: {orch_return}')
            print("------------------------------------------> END")
            break


