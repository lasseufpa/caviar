import subprocess
import signal
import threading
import time
import psutil

record_path = "/home/fhb/Documents/caviar_records"

experiment_id = "for_03uavs_03.2"
interval = 0.2

class runNatsServer(threading.Thread):
    def __init__(
        self,
    ):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runNatsServer")
        global nats_simu
        nats_simu = subprocess.Popen(["psrecord",
                                      "nats-server",
                                      "--log",
                                      record_path + "/" + experiment_id+"_nats.txt",
                                      "--interval",
                                      str(interval),
                                      "--include-children"])


class runAirSim(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runAirSim")
        global airsim_simu
        airsim_simu = subprocess.Popen(
            ["psrecord",
             "/home/fhb/Downloads/central_park/LinuxNoEditor/central_park/Binaries/Linux/central_park-Linux-DebugGame "+
             "-WINDOWED "+
             "-ResX=640 "+
             "-ResY=480",
             "--log",
             record_path + "/" + experiment_id+"_airsim.txt",
             "--interval",
             str(interval),
             "--include-children"]
        )


class runMobility(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runMobility")
        global mobility_simu
        mobility_simu = subprocess.Popen(
            [   "psrecord",
                "/home/fhb/miniconda3/envs/tf/bin/python " +
                "/home/fhb/git/caviar/examples/airsimTools/caviar_benchmark.py",
                "--log",
                record_path + "/" + experiment_id+"_mobility.txt",
                "--interval",
                str(interval),
                "--include-children"]
        )

class recordGPU(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runMobility")
        global gpu_simu
        gpu_simu = subprocess.Popen(
                [   "watch",
                    "-n",
                    "0.2",
                    "nvidia-smi",
                    "pmon",
                    "-c",
                    "1",
                    "|",
                    "tee",
                    "--append",
                    record_path + "/" + experiment_id+"_gpu.txt"]
            )

class runSionna(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("-----------> runSionna")
        global sionna_simu
        sionna_simu = subprocess.Popen(
            [   "psrecord",
                "/home/fhb/miniconda3/envs/tf/bin/python "+
                "/home/fhb/git/caviar/examples/sionna/followPath.py",
                "--log",
                record_path + "/" + experiment_id+"_sionna.txt",
                "--interval",
                str(interval),
                "--include-children"
            ]
        )


if __name__ == "__main__":
    orchestrator_thread = runNatsServer()
    threeD_thread = runAirSim()
    mobility_thread = runMobility()
    communications_thread = runSionna()
    record_gpu = recordGPU()

    try:
        orch_return = orchestrator_thread.start()
        threeD_thread.start()
        time.sleep(2)
        mobility_thread.start()
        time.sleep(2)
        communications_thread.start()
        time.sleep(2)
        # record_gpu.start()
        time.sleep(2)
    except Exception as e:
        print(f"Error: {str(e)}")
    
    while True:
        res = "A" #input("Press 'w' to close")
        print("#############################")
        print(f"#################: {mobility_simu.communicate()}")
        print("#############################")
        if res == "w" or (mobility_simu.communicate()[0] is None):
            print("The Program is terminated manually!")
            time.sleep(5)
            for child in psutil.Process(airsim_simu.pid).children(recursive=True):
                child.kill()
            airsim_simu.send_signal(signal.SIGTERM)
            time.sleep(2)
            for child in psutil.Process(nats_simu.pid).children(recursive=True):
                child.kill()
            nats_simu.send_signal(signal.SIGTERM)
            # for child in psutil.Process(mobility_simu.pid).children(recursive=True):
            #     child.kill()
            # mobility_simu.send_signal(signal.SIGTERM)
            for child in psutil.Process(sionna_simu.pid).children(recursive=True):
                child.kill()
            sionna_simu.send_signal(signal.SIGTERM)
            # for child in psutil.Process(gpu_simu.pid).children(recursive=True):
            #     child.kill()
            # gpu_simu.send_signal(signal.SIGTERM)
            print(f'orch_return: {orch_return}')
            print("------------------------------------------> END")
            break


