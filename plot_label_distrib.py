import os
import numpy as np
from joblib import load

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

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

plt.hist(train_labels, bins=50, label='Train', density=True)
plt.hist(test_labels, bins=50, label='Test', density=True, alpha=0.5)
# plt.grid(True)
# plt.xticks([1, 25, 50, 75, 100])

# plt.yticks(np.arange(round(top1_acc, 2), 100, 0.5))
# plt.xlim(1, 100)
# plt.ylim(top1_acc, 100)
plt.xlabel("Number of occurrences")
plt.ylabel("Beam indexes")
plt.legend()
plt.savefig("labels_distributions.png")