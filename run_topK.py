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

training = False
# training = True
current_version = 7

current_dir = os.getcwd()

if training:
    output_filename = os.path.join(current_dir, "allruns_v"+str(current_version)+".npz")
else:
    output_filename = os.path.join(current_dir, "new_test_set4.npz")

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

if training:
    from sklearn.preprocessing import LabelEncoder
    enc = LabelEncoder()
    enc.fit(possible_beam_pairs)

    from joblib import dump
    dump(enc, "trained_encoder_v"+str(current_version)+".joblib")
else:
    from joblib import load
    enc = load("trained_encoder_v"+str(current_version)+".joblib")

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
top25 = np.array(enc.transform(topk_pairs_per_scene[:, -25:].flatten())).reshape(
    topk_pairs_per_scene.shape[0], 25
)
top50 = np.array(enc.transform(topk_pairs_per_scene[:, -50:].flatten())).reshape(
    topk_pairs_per_scene.shape[0], 50
)
top75 = np.array(enc.transform(topk_pairs_per_scene[:, -75:].flatten())).reshape(
    topk_pairs_per_scene.shape[0], 75
)
top100 = np.array(enc.transform(topk_pairs_per_scene[:, -100:].flatten())).reshape(
    topk_pairs_per_scene.shape[0], 100
)
number_of_classes = enc.classes_.shape[0]

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

if training:
    rx_current_position, encoded_best_ray, top3, top5, top10, top25, top50, top75, top100 = shuffle(
        rx_current_position,
        encoded_best_ray,
        top3,
        top5,
        top10,
        top25,
        top50,
        top75,
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
        top25_train,
        top25_test,
        top50_train,
        top50_test,
        top75_train,
        top75_test,
        top100_train,
        top100_test,
    ) = train_test_split(
        rx_current_position,
        encoded_best_ray,
        top3,
        top5,
        top10,
        top25,
        top50,
        top75,
        top100,
        test_size=0.3,
        random_state=1,
        shuffle=False,
    )
else:
    X_test, y_test, top3_test, top5_test, top10_test, top25_test, top50_test, top75_test, top100_test = shuffle(
        rx_current_position,
        encoded_best_ray,
        top3,
        top5,
        top10,
        top25,
        top50,
        top75,
        top100,
        random_state=1,
    )


if training:
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neural_network import MLPClassifier
    # v7
    # max_depth=10 52.21% | 3.44% 
    # max_depth=14 68.40% | 8.04% 
    # max_depth=15 70.49% | 13.79% (BEST)
    # max_depth=16 73.36% | 8.04% 
    # max_depth=17 75.39% | 6.32% 
    # v6
    # max_depth=18 73.73% | 11.49% (BEST)
    # max_depth=19 74.8%  | 3.4% 
    # max_depth=20 78%    | 4%
    clf = DecisionTreeClassifier(random_state=0, max_depth=15)
    # clf = DecisionTreeClassifier(random_state=0)
    # clf = RandomForestClassifier(
    #     n_estimators=200
    # )  # 76.21% top-1 accuracy (test set) | 98.647% top-1 accuracy (train set)
    # clf = MLPClassifier(random_state=1, hidden_layer_sizes=(64), max_iter=300)  # 45.55%

    clf.fit(X_train, y_train)

    dump(clf, "trained_model_v"+str(current_version)+".joblib")
else:
    clf = load("trained_model_v"+str(current_version)+".joblib")


y_pred = clf.predict(X_test)

from sklearn.metrics import classification_report, accuracy_score

print(classification_report(y_test, y_pred))
print(f"Accuracy: {accuracy_score(y_test, y_pred)*100} %")

# Now calculate the topK accuracy
is_top1 = []
is_top3 = []
is_top5 = []
is_top10 = []
is_top25 = []
is_top50 = []
is_top75 = []
is_top100 = []
for idx, pred in enumerate(y_pred):
    is_top1.append(pred == y_test[idx])
    is_top3.append(pred in top3_test[idx])
    is_top5.append(pred in top5_test[idx])
    is_top10.append(pred in top10_test[idx])
    is_top25.append(pred in top25_test[idx])
    is_top50.append(pred in top50_test[idx])
    is_top75.append(pred in top75_test[idx])
    is_top100.append(pred in top100_test[idx])

top1_acc = (is_top1.count(True)/len(y_pred))*100
top3_acc = (is_top3.count(True)/len(y_pred))*100
top5_acc = (is_top5.count(True)/len(y_pred))*100
top10_acc = (is_top10.count(True)/len(y_pred))*100
top25_acc = (is_top25.count(True)/len(y_pred))*100
top50_acc = (is_top50.count(True)/len(y_pred))*100
top75_acc = (is_top75.count(True)/len(y_pred))*100
top100_acc = (is_top100.count(True)/len(y_pred))*100

print(f"Top-1 accuracy: {(is_top1.count(True)/len(y_pred))*100} %")
print(f"Top-3 accuracy: {(is_top3.count(True)/len(y_pred))*100} %")
print(f"Top-5 accuracy: {(is_top5.count(True)/len(y_pred))*100} %")
print(f"Top-10 accuracy: {(is_top10.count(True)/len(y_pred))*100} %")
print(f"Top-25 accuracy: {(is_top25.count(True)/len(y_pred))*100} %")
print(f"Top-50 accuracy: {(is_top50.count(True)/len(y_pred))*100} %")
print(f"Top-75 accuracy: {(is_top75.count(True)/len(y_pred))*100} %")
print(f"Top-100 accuracy: {(is_top100.count(True)/len(y_pred))*100} %")

print(f'clf.get_depth(): {clf.get_depth()}')

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

plt.plot([1, 3, 5, 10, 25, 50, 75, 100], [top1_acc,top3_acc,top5_acc,top10_acc, top25_acc, top50_acc,top75_acc,top100_acc])
plt.grid(True)
plt.xticks([1, 25, 50, 75, 100])

# plt.yticks(np.arange(round(top1_acc, 2), 100, 0.5))
plt.xlim(1, 100)
plt.ylim(top1_acc, 100)
plt.xlabel("K values")
plt.ylabel("Accuracy (%)")
plt.savefig("a.png")

################################## Sionna v0.15.1
# NLOS: 1274 elements (alias v7) (removing three outlier beams indexes)
# Accuracy: 70.49608355091384 %
# Top-1 accuracy: 70.49608355091384 %
# Top-3 accuracy: 83.5509138381201 %
# Top-5 accuracy: 85.37859007832898 %
# Top-10 accuracy: 86.42297650130548 %
# Top-25 accuracy: 89.55613577023499 %
# Top-50 accuracy: 92.16710182767625 %
# Top-75 accuracy: 95.03916449086162 %
# Top-100 accuracy: 95.822454308094 %
# clf.get_depth(): 15

# test new_test_set4 (SAR path)
# Accuracy: 38.582677165354326 %
# Top-1 accuracy: 38.582677165354326 %
# Top-3 accuracy: 55.118110236220474 %
# Top-5 accuracy: 60.629921259842526 %
# Top-10 accuracy: 63.77952755905512 %
# Top-25 accuracy: 68.50393700787401 %
# Top-50 accuracy: 77.16535433070865 %
# Top-75 accuracy: 84.25196850393701 %
# Top-100 accuracy: 85.03937007874016 %
# clf.get_depth(): 15

################################## Sionna v0.15.1
# NLOS: 1444 elements (alias v7)

# train/test allruns_v7
# Accuracy: 70.49608355091384 %
# Top-1 accuracy: 70.49608355091384 %
# Top-3 accuracy: 83.5509138381201 %
# Top-5 accuracy: 85.37859007832898 %
# Top-10 accuracy: 86.42297650130548 %
# Top-25 accuracy: 89.55613577023499 %
# Top-50 accuracy: 92.16710182767625 %
# Top-75 accuracy: 95.03916449086162 %
# Top-100 accuracy: 95.822454308094 %
# clf.get_depth(): 15


# test test_set (SAR path)
# Accuracy: 13.793103448275861 %
# Top-1 accuracy: 13.793103448275861 %
# Top-3 accuracy: 23.563218390804597 %
# Top-5 accuracy: 28.160919540229884 %
# Top-10 accuracy: 33.33333333333333 %
# Top-25 accuracy: 40.804597701149426 %
# Top-50 accuracy: 50.0 %
# Top-75 accuracy: 62.643678160919535 %
# Top-100 accuracy: 71.26436781609196 %
# clf.get_depth(): 15

################################## Sionna v0.15.1
# NLOS: 1444 elements (alias v6)

# train/test allruns_v6
# Accuracy: 76.95852534562212 %
# Top-1 accuracy: 76.95852534562212 %
# Top-3 accuracy: 92.16589861751152 %
# Top-5 accuracy: 94.47004608294931 %
# Top-10 accuracy: 96.31336405529954 %
# Top-25 accuracy: 96.7741935483871 %
# Top-50 accuracy: 97.6958525345622 %
# Top-75 accuracy: 97.6958525345622 %
# Top-100 accuracy: 97.6958525345622 %
# clf.get_depth(): 26


# test test_set (SAR path)
# Accuracy: 4.6875 %
# Top-1 accuracy: 4.6875 %
# Top-3 accuracy: 11.458333333333332 %
# Top-5 accuracy: 17.1875 %
# Top-10 accuracy: 23.4375 %
# Top-25 accuracy: 35.9375 %
# Top-50 accuracy: 43.75 %
# Top-75 accuracy: 60.9375 %
# Top-100 accuracy: 71.875 %
# clf.get_depth(): 26

################################## Sionna v0.15.1
# NLOS: 1964 elements (alias v5)

# train/test allruns_v4
# Accuracy: 69.83050847457626 %
# Top-1 accuracy: 69.83050847457626 %
# Top-3 accuracy: 79.3220338983051 %
# Top-5 accuracy: 82.20338983050848 %
# Top-10 accuracy: 84.40677966101696 %
# Top-25 accuracy: 86.10169491525423 %
# Top-50 accuracy: 89.32203389830508 %
# Top-75 accuracy: 90.67796610169492 %
# Top-100 accuracy: 92.03389830508475 %
# clf.get_depth(): 15


# test test_set (SAR path)
# Accuracy: 3.6458333333333335 %
# Top-1 accuracy: 3.6458333333333335 %
# Top-3 accuracy: 12.5 %
# Top-5 accuracy: 18.229166666666664 %
# Top-10 accuracy: 24.479166666666664 %
# Top-25 accuracy: 35.41666666666667 %
# Top-50 accuracy: 42.1875 %
# Top-75 accuracy: 48.4375 %
# Top-100 accuracy: 54.6875 %
# clf.get_depth(): 15

################################## Sionna v0.15.1
# NLOS: 1964 elements (alias v4)

# train/test allruns_v4

# Accuracy: 86.77966101694915 %
# Top-1 accuracy: 86.77966101694915 %
# Top-3 accuracy: 95.9322033898305 %
# Top-5 accuracy: 96.94915254237289 %
# Top-10 accuracy: 97.96610169491525 %
# Top-25 accuracy: 98.47457627118644 %
# Top-50 accuracy: 98.64406779661017 %
# Top-75 accuracy: 98.8135593220339 %
# Top-100 accuracy: 98.98305084745763 %
# clf.get_depth(): 25


# test test_set (SAR path)
# Accuracy: 2.604166666666667 %
# Top-1 accuracy: 2.604166666666667 %
# Top-3 accuracy: 10.416666666666668 %
# Top-5 accuracy: 15.625 %
# Top-10 accuracy: 21.354166666666664 %
# Top-25 accuracy: 30.729166666666668 %
# Top-50 accuracy: 40.10416666666667 %
# Top-75 accuracy: 55.729166666666664 %
# Top-100 accuracy: 69.27083333333334 %
# clf.get_depth(): 25

################################## Sionna v0.15.1
# NLOS: 1313 elements (alias v3)

# Top-1 accuracy: 84.26395939086294 %
# Top-3 accuracy: 95.43147208121827 %
# Top-5 accuracy: 97.96954314720813 %
# Top-10 accuracy: 98.47715736040608 %
# Top-25 accuracy: 98.73096446700508 %
# Top-50 accuracy: 98.73096446700508 %
# Top-75 accuracy: 98.98477157360406 %
# Top-100 accuracy: 99.23857868020305 %
# clf.get_depth(): 19

################################## Sionna v0.15.0
# NLOS: 1947 elements (alias v2) (Added around 450 runs close to the ground for better performance on SAR)

# Top-1 accuracy: 87.86324786324786 %
# Top-3 accuracy: 97.09401709401709 %
# Top-5 accuracy: 97.77777777777777 %
# Top-10 accuracy: 98.29059829059828 %
# Top-25 accuracy: 98.97435897435898 %
# Top-50 accuracy: 98.97435897435898 %
# Top-75 accuracy: 99.31623931623932 %
# Top-100 accuracy: 99.48717948717949 %
# clf.get_depth(): 25

# --------------------------------------------------

# NLOS: 1495 elements (alias v1)

# Top-1 accuracy: 93.76391982182628 %
# Top-3 accuracy: 98.66369710467706 %
# Top-5 accuracy: 98.88641425389754 %
# Top-10 accuracy: 98.88641425389754 %
# Top-50 accuracy: 99.33184855233853 %
# Top-75 accuracy: 99.33184855233853 %
# Top-100 accuracy: 99.55456570155901 %
# clf.get_depth(): 17


# NLOS: 816 elements

# Top-1 accuracy: 89.79591836734694 %
# Top-3 accuracy: 97.14285714285714 %
# Top-5 accuracy: 98.36734693877551 %
# Top-10 accuracy: 99.18367346938776 %
# Top-50 accuracy: 99.59183673469387 %
# Top-100 accuracy: 100.0 %
# clf.get_depth(): 20

################################## Sionna v0.14.0

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