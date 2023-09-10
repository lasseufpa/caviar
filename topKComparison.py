import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set_theme()

top1_acc_sar = 0.385826
top2_acc_sar = 0.511811
top3_acc_sar = 0.551181
top4_acc_sar = 0.606299
top5_acc_sar = 0.606299
top6_acc_sar = 0.614173
top7_acc_sar = 0.614173
top8_acc_sar = 0.629921
top9_acc_sar = 0.629921
top10_acc_sar = 0.637795
top25_acc_sar = 0.685039
top50_acc_sar = 0.771653
top75_acc_sar = 0.842519
top100_acc_sar = 0.850393

top1_acc_vis = 0.38
top2_acc_vis = 0.46
top3_acc_vis = 0.52
top4_acc_vis = 0.55
top5_acc_vis = 0.58
top6_acc_vis = 0.60
top7_acc_vis = 0.61
top8_acc_vis = 0.63
top9_acc_vis = 0.64
top10_acc_vis = 0.65

plt.plot(
    [1, 3, 5, 10, 25, 50, 75, 100],
    [
        top1_acc_train,
        top3_acc_train,
        top5_acc_train,
        top10_acc_train,
        top25_acc_train,
        top50_acc_train,
        top75_acc_train,
        top100_acc_train,
    ],
    marker="x",
    label="Train",
)

plt.plot(
    [1, 3, 5, 10, 25, 50, 75, 100],
    [
        top1_acc_sar,
        top3_acc_sar,
        top5_acc_sar,
        top10_acc_sar,
        top25_acc_sar,
        top50_acc_sar,
        top75_acc_sar,
        top100_acc_sar,
    ],
    marker="*",
    label="Search and rescue",
)

plt.grid(True)
plt.xticks([1, 10, 25, 50, 75, 100])
plt.legend()
plt.yticks(np.arange(35, 101, 5))
plt.xlim(0, 101)
plt.ylim(35, 100)
plt.xlabel("K values")
plt.ylabel("Accuracy (%)")
plt.savefig("topk_results.png")


plt.plot(
    np.arange(1, 11, 1),
    [
        top1_acc_sar,
        top2_acc_sar,
        top3_acc_sar,
        top4_acc_sar,
        top5_acc_sar,
        top6_acc_sar,
        top7_acc_sar,
        top8_acc_sar,
        top9_acc_sar,
        top10_acc_sar,
    ],
    marker="*",
    label="Our method on the search and rescue set",
    color="red",
)

plt.plot(
    np.arange(1, 11, 1),
    [
        top1_acc_vis,
        top2_acc_vis,
        top3_acc_vis,
        top4_acc_vis,
        top5_acc_vis,
        top6_acc_vis,
        top7_acc_vis,
        top8_acc_vis,
        top9_acc_vis,
        top10_acc_vis,
    ],
    marker="x",
    label="Visual aided method",
    color="blue",
)

plt.grid(True)
plt.xticks(np.arange(1, 11, 1))
plt.legend()
plt.yticks(np.arange(0.2, 1.1, 0.1))
plt.xlim(0.95, 10.05)
plt.ylim(0.1, 1)
plt.xlabel("K values")
plt.ylabel("Accuracy (%)")
plt.title("Performance comparison (NLOS)")
plt.savefig("topk_results_comparison.png")

# train
# Top-1 accuracy: 70.49608355091384 %
# Top-2 accuracy: 80.93994778067885 %
# Top-3 accuracy: 83.5509138381201 %
# Top-4 accuracy: 85.11749347258485 %
# Top-5 accuracy: 85.37859007832898 %
# Top-6 accuracy: 85.90078328981723 %
# Top-7 accuracy: 85.90078328981723 %
# Top-8 accuracy: 85.90078328981723 %
# Top-9 accuracy: 86.16187989556136 %
# Top-10 accuracy: 86.42297650130548 %
# Top-25 accuracy: 89.55613577023499 %
# Top-50 accuracy: 92.16710182767625 %
# Top-75 accuracy: 95.03916449086162 %
# Top-100 accuracy: 95.822454308094 %

# SAR
# Top-1 accuracy: 38.582677165354326 %
# Top-2 accuracy: 51.181102362204726 %
# Top-3 accuracy: 55.118110236220474 %
# Top-4 accuracy: 60.629921259842526 %
# Top-5 accuracy: 60.629921259842526 %
# Top-6 accuracy: 61.417322834645674 %
# Top-7 accuracy: 61.417322834645674 %
# Top-8 accuracy: 62.99212598425197 %
# Top-9 accuracy: 62.99212598425197 %
# Top-10 accuracy: 63.77952755905512 %
# Top-25 accuracy: 68.50393700787401 %
# Top-50 accuracy: 77.16535433070865 %
# Top-75 accuracy: 84.25196850393701 %
# Top-100 accuracy: 85.03937007874016 %
