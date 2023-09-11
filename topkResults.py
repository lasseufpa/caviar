import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set_theme()

top1_acc_train = 70.4960
top2_acc_train = 80.9399
top3_acc_train = 83.550
top4_acc_train = 85.1174
top5_acc_train = 85.3785
top6_acc_train = 85.9007
top7_acc_train = 85.9007
top8_acc_train = 85.9007
top9_acc_train = 86.1618
top10_acc_train = 86.4229
top25_acc_train = 89.5561
top50_acc_train = 92.1671
top75_acc_train = 95.0391
top100_acc_train = 95.8224

top1_acc_sar = 38.5826
top2_acc_sar = 51.1811
top3_acc_sar = 55.1181
top4_acc_sar = 60.6299
top5_acc_sar = 60.6299
top6_acc_sar = 61.4173
top7_acc_sar = 61.4173
top8_acc_sar = 62.9921
top9_acc_sar = 62.9921
top10_acc_sar = 63.7795
top25_acc_sar = 68.5039
top50_acc_sar = 77.1653
top75_acc_sar = 84.2519
top100_acc_sar = 85.0393

# plt.plot(
#     [1, 3, 5, 10, 25, 50, 75, 100],
#     [
#         top1_acc_train,
#         top3_acc_train,
#         top5_acc_train,
#         top10_acc_train,
#         top25_acc_train,
#         top50_acc_train,
#         top75_acc_train,
#         top100_acc_train,
#     ],
#     marker="x",
#     label="Train",
# )

# plt.plot(
#     [1, 3, 5, 10, 25, 50, 75, 100],
#     [
#         top1_acc_sar,
#         top3_acc_sar,
#         top5_acc_sar,
#         top10_acc_sar,
#         top25_acc_sar,
#         top50_acc_sar,
#         top75_acc_sar,
#         top100_acc_sar,
#     ],
#     marker="*",
#     label="Search and rescue",
# )

# plt.grid(True)
# plt.xticks([1, 10, 25, 50, 75, 100])
# plt.legend()
# plt.yticks(np.arange(35, 101, 5))
# plt.xlim(0, 101)
# plt.ylim(3, 100)
# plt.xlabel("K values")
# plt.ylabel("Accuracy (%)")
# plt.savefig("topk_results.png")

plt.plot(
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100],
    [
        top1_acc_train,
        top2_acc_train,
        top3_acc_train,
        top4_acc_train,
        top5_acc_train,
        top6_acc_train,
        top7_acc_train,
        top8_acc_train,
        top9_acc_train,
        top10_acc_train,
        top25_acc_train,
        top50_acc_train,
        top75_acc_train,
        top100_acc_train,
    ],
    marker="x",
    label="Test set",
)

plt.plot(
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 25, 50, 75, 100],
    [
        top1_acc_sar,
        top1_acc_sar,
        top3_acc_sar,
        top4_acc_sar,
        top5_acc_sar,
        top6_acc_sar,
        top7_acc_sar,
        top8_acc_sar,
        top9_acc_sar,
        top10_acc_sar,
        top25_acc_sar,
        top50_acc_sar,
        top75_acc_sar,
        top100_acc_sar,
    ],
    marker="*",
    label="Search and rescue",
)

x_ticks = np.arange(0, 101, 10)
x_ticks[0] = 1
plt.grid(True)
plt.xticks(x_ticks)
plt.legend()
plt.yticks(np.arange(35, 101, 5))
plt.xlim(0, 101)
plt.ylim(35, 100)
plt.xlabel("K values")
plt.ylabel("Accuracy (%)")
plt.savefig("topk_results.png")

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
