import os
import numpy as np
from joblib import load
import matplotlib.pyplot as plt

current_dir = os.getcwd()

enc = load("trained_encoder.joblib")

train_set_filename = os.path.join(current_dir, "allruns_v4.npz")
train_set = np.load(train_set_filename, allow_pickle=True)
train_features = train_set["rx_current_position"]
train_labels_raw = train_set["best_ray"]
train_labels_pre_encoding = [str([ray[0][0], ray[0][1]]) for ray in train_labels_raw]
train_labels = enc.transform(train_labels_pre_encoding)

test_set_filename = os.path.join(current_dir, "test_set.npz")
test_set = np.load(test_set_filename, allow_pickle=True)
test_features = test_set["rx_current_position"]
test_labels_raw = test_set["best_ray"]
test_labels_pre_encoding = [str([ray[0][0], ray[0][1]]) for ray in test_labels_raw]
test_labels = enc.transform(test_labels_pre_encoding)

indexes_of_interest = np.argwhere((train_labels == 197))

outlier_positions = train_features[indexes_of_interest]


import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

plt.hist(outlier_positions[:, 0, 0])
plt.xlabel("Number of occurrences")
plt.ylabel("X positions")
plt.savefig("x_pos.png")

plt.figure()
plt.hist(outlier_positions[:, 0, 1])
plt.xlabel("Number of occurrences")
plt.ylabel("Y positions")
plt.savefig("y_pos.png")

print("END")

# beam_occurrences = []
# for i in range(256):
#     beam_occurrences.append(np.count_nonzero(train_labels == i))
#     print(f'Beam #{i}: {np.count_nonzero(train_labels == i)} occurrences')

# print(f'Most repeated value = {np.argmax(beam_occurrences)}')
