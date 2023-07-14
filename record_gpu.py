from nvitop import Device, GpuProcess, NA, colored
import time
devices = Device.all()  # or `Device.cuda.all()` to use CUDA ordinal instead
out_file = open("/home/fhb/Documents/caviar_records/gpu_full.txt", "w")
out_file.write("pid" + ";" + "command" + ";" + "gpu_memory" + ";" + "gpu_sm_utilization" + "\n")

while True:
    for device in devices:
        processes = device.processes()  # type: Dict[int, GpuProcess]
        processes = GpuProcess.take_snapshots(processes.values(), failsafe=True)
        processes.sort(key=lambda process: (process.username, process.pid))

        for snapshot in processes:
                if "/usr/" in str(snapshot.command):
                     pass
                else:
                    print(snapshot)
                    out_file.write(str(snapshot.pid) + ";" + str(snapshot.command) + ";" + str(snapshot.gpu_memory_human) + ";" + str(snapshot.gpu_sm_utilization) + "\n")
    #time.sleep(0.1)

out_file.close()
