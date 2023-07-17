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
output_filename = os.path.join(current_dir, "allruns.npz")
caviar_output = np.load(output_filename, allow_pickle=True)

rx_current_position = caviar_output["rx_current_position"]
best_ray = caviar_output["best_ray"]
equivalentChannelMagnitudes = caviar_output["equivalentChannelMagnitude"]

k = 100
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
top50 = np.array(enc.transform(topk_pairs_per_scene[:, -50:].flatten())).reshape(
    topk_pairs_per_scene.shape[0], 50
)
top100 = np.array(enc.transform(topk_pairs_per_scene[:, -100:].flatten())).reshape(
    topk_pairs_per_scene.shape[0], 100
)
number_of_classes = enc.classes_.shape[0]

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

rx_current_position, encoded_best_ray, top3, top5, top10, top50, top100 = shuffle(
    rx_current_position,
    encoded_best_ray,
    top3,
    top5,
    top10,
    top50,
    top100,
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
    top50_train,
    top50_test,
    top100_train,
    top100_test,
) = train_test_split(
    rx_current_position,
    encoded_best_ray,
    top3,
    top5,
    top10,
    top50,
    top100,
    test_size=0.3,
    random_state=1,
    shuffle=False,
)

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

clf = DecisionTreeClassifier(random_state=0)
# clf = RandomForestClassifier(
#     n_estimators=200
# )  # 76.21% top-1 accuracy (test set) | 98.647% top-1 accuracy (train set)
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
is_top50 = []
is_top100 = []
for idx, pred in enumerate(y_pred):
    is_top1.append(pred == y_test[idx])
    is_top3.append(pred in top3_test[idx])
    is_top5.append(pred in top5_test[idx])
    is_top10.append(pred in top10_test[idx])
    is_top50.append(pred in top50_test[idx])
    is_top100.append(pred in top100_test[idx])

print(f"Top-1 accuracy: {(is_top1.count(True)/len(y_pred))*100} %")
print(f"Top-3 accuracy: {(is_top3.count(True)/len(y_pred))*100} %")
print(f"Top-5 accuracy: {(is_top5.count(True)/len(y_pred))*100} %")
print(f"Top-10 accuracy: {(is_top10.count(True)/len(y_pred))*100} %")
print(f"Top-50 accuracy: {(is_top50.count(True)/len(y_pred))*100} %")
print(f"Top-100 accuracy: {(is_top100.count(True)/len(y_pred))*100} %")

from joblib import dump

dump(clf, "trained_model.joblib")
dump(enc, "trained_encoder.joblib")

print(f'clf.get_depth(): {clf.get_depth()}')

# NLOS: 214 elements

# Default Decision Tree
# Top-1 accuracy: 69.61325966850829 %
# Top-3 accuracy: 74.58563535911603 %
# Top-5 accuracy: 75.13812154696133 %
# Top-10 accuracy: 78.45303867403315 %
# clf.get_depth(): 15

# NLOS: 639 elements

# Default Decision Tree
# Top-1 accuracy: 68.22916666666666 %
# Top-3 accuracy: 82.29166666666666 %
# Top-5 accuracy: 84.375 %
# Top-10 accuracy: 86.45833333333334 %
# Top-50 accuracy: 89.58333333333334 %
# Top-100 accuracy: 92.70833333333334 %
# clf.get_depth(): 23
# -----------------------------------------------------


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