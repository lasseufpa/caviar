import numpy as np
import os
from matplotlib import pyplot as plt 

current_dir = os.getcwd()

####################################### General throughputs ################################ 
dataset_file = os.path.join(current_dir, "bit_rates.npz")
caviar_output = np.load(dataset_file, allow_pickle=True)
bit_rates_bps = caviar_output["bit_rate"]
bit_rates_Gbps = bit_rates_bps / 1e9
general_throughputs = bit_rates_Gbps.flatten()
####################################### Optimal and Random "agents" throughputs ################################
dataset_file = os.path.join(current_dir, "obtained_bit_rates_Gbps.npz")
obtained_bit_rates_Gbps = np.load(dataset_file, allow_pickle=True)
best_bit_rates_Gbps = obtained_bit_rates_Gbps["best_bit_rates_Gbps"]
random_bit_rates_Gbps = obtained_bit_rates_Gbps["random_bit_rates_Gbps"]
############################################################################################
plt.figure()
plt.hist(general_throughputs, bins=1000, label="In general")
plt.hist(best_bit_rates_Gbps, bins=100, label="Best")
plt.hist(random_bit_rates_Gbps, bins=100, label="Random")
plt.title("Throughputs (Gbps)")
plt.legend()
plt.savefig("throughputs.png")

print("--------------------- In general ---------------------------")
print(f'max: {np.max(bit_rates_Gbps)} Gbps')
print(f'min: {np.min(bit_rates_Gbps)} Gbps')
print(f'mean: {np.mean(bit_rates_Gbps)} Gbps')
print("--------------------- Best ---------------------------")
print(f'max: {np.max(best_bit_rates_Gbps)} Gbps')
print(f'min: {np.min(best_bit_rates_Gbps)} Gbps')
print(f'mean: {np.mean(best_bit_rates_Gbps)} Gbps')
print("--------------------- Random ---------------------------")
print(f'max: {np.max(random_bit_rates_Gbps)} Gbps')
print(f'min: {np.min(random_bit_rates_Gbps)} Gbps')
print(f'mean: {np.mean(random_bit_rates_Gbps)} Gbps')
