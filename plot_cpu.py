import numpy as np
import matplotlib

# matplotlib.use("pgf")
# matplotlib.rcParams.update(
#     {
#         "pgf.texsystem": "pdflatex",
#         "font.name": "Times",
#         "text.usetex": True,
#         "pgf.rcfonts": False,
#     }
# )
# matplotlib.rc("xtick", labelsize=8)
# matplotlib.rc("ytick", labelsize=8)
from matplotlib import pyplot as plt
import seaborn as sns

sns.set_theme()

colors = sns.color_palette("deep")
simtype = "1uavs"
simode = "newgpu"


def moving_average(x, w):
    return np.convolve(x, np.ones(w), "valid") / w


def plot_individual(n_users):
    with open(
        "./output/caviar_records/for_"
        + str(n_users)
        + "uavs_"
        + simode
        + "_airsim.txt",
        "r",
    ) as file:
        lines = file.readlines()
        line_array = []
        for line in lines[1:]:
            line_array.append(line.split())
    unreal = np.array(line_array, dtype=float)

    with open(
        "./output/caviar_records/for_"
        + str(n_users)
        + "uavs_"
        + simode
        + "_mobility.txt",
        "r",
    ) as file:
        lines = file.readlines()
        line_array = []
        for line in lines[1:]:
            line_array.append(line.split())
    airsim = np.array(line_array, dtype=float)

    with open(
        "./output/caviar_records/for_"
        + str(n_users)
        + "uavs_"
        + simode
        + "_sionna.txt",
        "r",
    ) as file:
        lines = file.readlines()
        line_array = []
        for line in lines[1:]:
            line_array.append(line.split())
    yolo = np.array(line_array, dtype=float)

    with open(
        "./output/caviar_records/for_"
        + str(n_users)
        + "uavs_"
        + simode
        + "_nats.txt",
        "r",
    ) as file:
        lines = file.readlines()
        line_array = []
        for line in lines[1:]:
            line_array.append(line.split())
    ns3 = np.array(line_array, dtype=float)

    lenght_limit = airsim.shape[0]

    unreal = unreal[:lenght_limit]
    airsim = airsim[:lenght_limit]
    yolo = yolo[:lenght_limit]
    ns3 = ns3[:lenght_limit]

    unreal_cpu = moving_average(unreal[:, 1], 25) / 12
    airsim_cpu = moving_average(airsim[:, 1], 25) / 12
    yolo_cpu = moving_average(yolo[:, 1], 25) / 12
    ns3_cpu = moving_average(ns3[:, 1], 25) / 12
    time = moving_average(ns3[:, 0], 25)
    Total = unreal_cpu + airsim_cpu + yolo_cpu + ns3_cpu

    # plt.figure(figsize=(3.2,2.2))
    print(len(ns3))
    plt.xlabel("Elapsed time (s)")
    plt.ylabel("CPU (%)")
    plt.xlim(-1, time.max() + time.max() * 0.02)
    plt.ylim(-2, 120)
    plt.xticks(np.arange(0, time.max() + time.max() * 0.02, 100))
    plt.plot(time, Total, label="Total", color=colors[5])
    plt.plot(time, unreal_cpu, label="3D module", color=colors[0])
    plt.plot(time, airsim_cpu, label="AI module", color=colors[1])
    plt.plot(time, yolo_cpu, label="Comm. module", color=colors[3])
    plt.plot(time, ns3_cpu, label="NATS", color=colors[2])

    # airsim_cpu.resize(unreal_cpu.shape,refcheck=False)
    # yolo_cpu.resize(unreal_cpu.shape,refcheck=False)
    # ns3_cpu.resize(unreal_cpu.shape,refcheck=False)

    # plt.legend()
    plt.legend(loc="upper right")
    # plt.grid()
    plt.tight_layout()
    # plt.savefig('../figures/graphs/results_cpu/'+str(n_users)+'users_CPU_'+simtype+'.pgf')
    # plt.savefig(
    #     "./output/caviar_records/" + str(n_users) + "_" + simode + ".pdf"
    # )
    plt.savefig(
        "./output/Figures/cpu_"
        + str(n_users)
        + ".pdf"
    )
    plt.close()

    return ns3_cpu, time


# totals = []
# times = []
# for x in range(5, 45, 5):
#   totals.append(plot_individual(x)[0])
#   times.append(plot_individual(x)[1])

# plot_individual(1)
# plot_individual(2)
plot_individual(1)
plot_individual(2)
plot_individual(3)
plot_individual(4)
plot_individual(5)


# plt.figure(figsize=(3.8,2.8))
# plt.xlabel("Elapsed time (s)")
# plt.ylabel('CPU (%)')
# plt.ylim(0, 10)
# plt.plot(times[7],totals[7], marker='', label='40 UEs', color=colors[8])
# plt.plot(times[6],totals[6], marker='', label='35 UEs', color=colors[7])
# plt.plot(times[5],totals[5], marker='', label='30 UEs', color=colors[6])
# plt.plot(times[4],totals[4], marker='', label='25 UEs', color=colors[5])
# plt.plot(times[3],totals[3], marker='', label='20 UEs', color=colors[3])
# plt.plot(times[2],totals[2], marker='', label='15 UEs', color=colors[2])
# plt.plot(times[1],totals[1], marker='', label='10 UEs', color=colors[1])
# plt.plot(times[0],totals[0], marker='', label='5 UEs', color=colors[0])

# plt.legend(loc='lower right')
# plt.grid()

# plt.tight_layout()
# #plt.savefig('../figures/graphs/results_cpu/ns3_cpu_'+simtype+'.pgf')
# plt.savefig('/home/joao/paper_plots/cpu/ns3_cpu_'+simtype+'.png')
# plt.close()
