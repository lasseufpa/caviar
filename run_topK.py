def getTopK(topK, dataset):
    """
    Receives an multidimensional array of the equivalent channel magnitudes
    for each scene and returns the top-K beam pairs for each scene
    # Input shape: [nScenes, nRx, nTx] -> Output shape: [nScenes, topK]
    """
    output = []
    number_of_scenes = dataset.shape[0]
    for scene in range(number_of_scenes):  # iterates over all scenes
        channel_magnitudes_in_scene = dataset[scene, :, :]
        biggest_channel_magnitudes_in_scene = np.sort(
            channel_magnitudes_in_scene, axis=None
        )
        # appends a list containing the indices of the k highest values in crescent order
        output.append(
            [
                str([np.argwhere(k == channel_magnitudes_in_scene)[0][0],
                     np.argwhere(k == channel_magnitudes_in_scene)[0][1]])
                for k in biggest_channel_magnitudes_in_scene[-topK:]
            ]
        )
    return np.array(output).reshape(number_of_scenes, topK)


import numpy as np
import os

current_dir = os.getcwd()
output_filename = os.path.join(current_dir, "output_with_imgs.npz")
caviar_output = np.load(output_filename, allow_pickle=True)

rx_current_position = caviar_output["rx_current_position"]
best_ray = caviar_output["best_ray"]
equivalentChannelMagnitudes = caviar_output["equivalentChannelMagnitude"]

k = 10
n_rx = 4
n_tx = 64
possible_beam_pairs = [str([r, t]) for r in range(n_rx) for t in range(n_tx)]

topk_pairs_per_scene = getTopK(k, equivalentChannelMagnitudes)

best_ray_true = [str([ray[0][0], ray[0][1]]) for ray in best_ray]

from sklearn.preprocessing import LabelEncoder

enc = LabelEncoder()
enc.fit(possible_beam_pairs)
encoded_best_ray = enc.transform(best_ray_true)

top3 = np.array(enc.transform(topk_pairs_per_scene[:, -3:].flatten())).reshape(
    topk_pairs_per_scene.shape[0], 3
)
top5 = np.array(enc.transform(topk_pairs_per_scene[:, -5:].flatten())).reshape(
    topk_pairs_per_scene.shape[0], 5
)
top10 = np.array(enc.transform(topk_pairs_per_scene[:, -10:].flatten())).reshape(
    topk_pairs_per_scene.shape[0], 10
)
number_of_classes = enc.classes_.shape[0]

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

rx_current_position, encoded_best_ray, top3, top5, top10 = shuffle(
    rx_current_position,
    encoded_best_ray,
    top3,
    top5,
    top10,
    random_state=1,
)

(
    X_train,
    X_test,
    y_train,
    y_test,
    top3_train,
    top3_test,
    top5_train,
    top5_test,
    top10_train,
    top10_test,
) = train_test_split(
    rx_current_position,
    encoded_best_ray,
    top3,
    top5,
    top10,
    test_size=0.3,
    random_state=1,
    shuffle=False,
)

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

# clf = DecisionTreeClassifier(random_state=0)
clf = RandomForestClassifier(
    n_estimators=300
)  # 76.21% top-1 accuracy (test set) | 98.647% top-1 accuracy (train set)
# clf = MLPClassifier(random_state=1, hidden_layer_sizes=(64), max_iter=300)  # 45.55%

clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

from sklearn.metrics import classification_report, accuracy_score

print(classification_report(y_test, y_pred))
print(f"Accuracy: {accuracy_score(y_test, y_pred)*100} %")

# Now calculate the topK accuracy
is_top1 = []
is_top3 = []
is_top5 = []
is_top10 = []
for idx, pred in enumerate(y_pred):
    is_top1.append(pred == y_test[idx])
    is_top3.append(pred in top3_test[idx])
    is_top5.append(pred in top5_test[idx])
    is_top10.append(pred in top10_test[idx])

print(f"Top-1 accuracy: {(is_top1.count(True)/len(y_pred))*100} %")
print(f"Top-3 accuracy: {(is_top3.count(True)/len(y_pred))*100} %")
print(f"Top-5 accuracy: {(is_top5.count(True)/len(y_pred))*100} %")
print(f"Top-10 accuracy: {(is_top10.count(True)/len(y_pred))*100} %")

from joblib import dump

dump(clf, "trained_tree_200_est.joblib")
dump(enc, "encoder.joblib")

# LOS: 427 elements | NLOS: 282 elements

# Random forest 200 estimators only LOS (test set)
# Accuracy: 69.76744186046511 %
# Top-1 accuracy: 69.76744186046511 %
# Top-3 accuracy: 80.62015503875969 %
# Top-5 accuracy: 82.17054263565892 %
# Top-10 accuracy: 84.49612403100775 %

# Random forest 200 estimators only LOS (train set)
# Accuracy: 96.97986577181209 %
# Top-1 accuracy: 96.97986577181209 %
# Top-3 accuracy: 96.97986577181209 %
# Top-5 accuracy: 96.97986577181209 %
# Top-10 accuracy: 96.97986577181209 %

# Random forest 200 estimators only NLOS (test set)
# Accuracy: 54.11764705882353 %
# Top-1 accuracy: 54.11764705882353 %
# Top-3 accuracy: 69.41176470588235 %
# Top-5 accuracy: 71.76470588235294 %
# Top-10 accuracy: 75.29411764705883 %

# Random forest 200 estimators only NLOS (train set)
# Accuracy: 100.0 %
# Top-1 accuracy: 100.0 %
# Top-3 accuracy: 100.0 %
# Top-5 accuracy: 100.0 %
# Top-10 accuracy: 100.0 %