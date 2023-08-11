import numpy as np
import os
from matplotlib import pyplot as plt
import seaborn as sns
from joblib import load

sns.set_theme()

current_dir = os.getcwd()
output_filename = os.path.join(current_dir, "allruns.npz")
caviar_output = np.load(output_filename, allow_pickle=True)

best_ray = caviar_output["best_ray"]
best_ray_true = [str([ray[0][0], ray[0][1]]) for ray in best_ray]

enc = load("trained_encoder.joblib")
encoded_best_ray = enc.transform(best_ray_true)
# pred_beam_index = []
# for pair in best_ray:
#     pred_beam_index.append(enc.transform(pair)[0][1:-1].split(","))
plt.figure()
plt.xlabel("Beam pair indexes")
plt.ylabel("Number of occurrences")
plt.ylim(0, 100)
plt.hist(encoded_best_ray, bins=100)
plt.savefig("beam_indexes_choices.png")
