import numpy as np
import os

rng = np.random.default_rng(1)

current_dir = os.getcwd()
dataset_file = os.path.join(current_dir, "bit_rates.npz")
caviar_output = np.load(dataset_file, allow_pickle=True)

bit_rates_bps = caviar_output["bit_rate"]
bit_rates_Gbps = bit_rates_bps / 1e9

best_rays_raw = caviar_output["best_ray"]
best_rays = np.array([ray[0] for ray in best_rays_raw])
best_rays_rx = best_rays[:, 0]
best_rays_tx = best_rays[:, 1]
best_bit_rates_Gbps = []
random_bit_rates_Gbps = []
for scene_number in range(len(bit_rates_bps)):
    best_bit_rates_Gbps.append(bit_rates_Gbps[scene_number, best_rays_rx[scene_number], best_rays_tx[scene_number]])
    random_bit_rates_Gbps.append(bit_rates_Gbps[scene_number, rng.integers(0,4), rng.integers(0,64)])

np.savez(
    "obtained_bit_rates_Gbps",
    best_bit_rates_Gbps=best_bit_rates_Gbps,
    random_bit_rates_Gbps=random_bit_rates_Gbps
)