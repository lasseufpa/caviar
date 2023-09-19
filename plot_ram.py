import numpy as np
import matplotlib
matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})
matplotlib.rc('xtick', labelsize=8) 
matplotlib.rc('ytick', labelsize=8) 
from matplotlib import pyplot as plt
import seaborn as sns

colors = sns.color_palette('deep')

sns.set_theme()

simode = 'nowait'

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

def plot_individual(n_users):

    with open('/home/fhb/Documents/caviar_records/for_'+str(n_users)+'uavs_'+simode+'_airsim.txt', 'r') as file:
        lines = file.readlines()
        line_array = []
        for line in lines[1:]:
            line_array.append(line.split())
    unreal = np.array(line_array, dtype=float)

    with open('/home/fhb/Documents/caviar_records/for_'+str(n_users)+'uavs_'+simode+'_mobility.txt', 'r') as file:
        lines = file.readlines()
        line_array = []
        for line in lines[1:]:
            line_array.append(line.split())
    airsim = np.array(line_array, dtype=float)

    with open('/home/fhb/Documents/caviar_records/for_'+str(n_users)+'uavs_'+simode+'_sionna.txt', 'r') as file:
        lines = file.readlines()
        line_array = []
        for line in lines[1:]:
            line_array.append(line.split())
    yolo = np.array(line_array, dtype=float)

    with open('/home/fhb/Documents/caviar_records/for_'+str(n_users)+'uavs_'+simode+'_nats.txt', 'r') as file:
        lines = file.readlines()
        line_array = []
        for line in lines[1:]:
            line_array.append(line.split())
    ns3 = np.array(line_array, dtype=float)

    # lenght_limit = yolo.shape[0]
    lenght_limit = airsim.shape[0]

    unreal = unreal[:lenght_limit]
    airsim = airsim[:lenght_limit]
    yolo = yolo[:lenght_limit]
    ns3 = ns3[:lenght_limit]

    unreal_ram = moving_average(unreal[:,2], 1)
    airsim_ram = moving_average(airsim[:,2], 1)
    yolo_ram = moving_average(yolo[:,2], 1)
    ns3_ram = moving_average(ns3[:,2], 1)
    time = moving_average(ns3[:,0], 1)


    #plt.figure(figsize=(3.6,2.6))

    plt.xlabel("Elapsed time (s)")
    plt.ylabel('Memory (MB)')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    #plt.ylim(0, 90)
    plt.plot(time,yolo_ram, marker='', label='Comm. mdule', color=colors[3])
    plt.plot(time,airsim_ram, marker='', label='AI module', color=colors[1])
    plt.plot(time,unreal_ram, marker='', label='3D module', color=colors[0])
    plt.plot(time,ns3_ram, marker='', label='NATS', color=colors[2])


    plt.legend(loc="lower right")
    # plt.grid()
    plt.tight_layout()
    #plt.savefig('Figures/'+str(n_users)+'users_CPU.png')
    # plt.savefig('../figures/graphs/results_ram/'+str(n_users)+'users_RAM_5uavs.pgf')
    plt.savefig('/home/fhb/Documents/caviar_records/ram_'+str(n_users)+'.pdf')
    plt.close()

    return ns3_ram

totals = []
# for x in range(5, 45, 5):
#   totals.append(plot_individual(x))

plot_individual(1)
plot_individual(2)
plot_individual(3)
plot_individual(4)
plot_individual(5)
