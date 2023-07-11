from nvitop import Device

devices = Device.all()  # or `Device.cuda.all()` to use CUDA ordinal instead
for device in devices:
    processes = device.processes()  # type: Dict[int, GpuProcess]
    sorted_pids = sorted(processes.keys())

    print(device)
    print(f'  - Fan speed:       {device.fan_speed()}%')
    print(f'  - Temperature:     {device.temperature()}C')
    print(f'  - GPU utilization: {device.gpu_utilization()}%')
    print(f'  - Total memory:    {device.memory_total_human()}')
    print(f'  - Used memory:     {device.memory_used_human()}')
    print(f'  - Free memory:     {device.memory_free_human()}')
    print(f'  - Processes ({len(processes)}): {sorted_pids}')
    for pid in sorted_pids:
        print(f'    - {processes[pid]}')
    print('-' * 120)