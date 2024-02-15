import json
import os
import numpy as np
from matplotlib import pyplot as plt
import scipy
from scipy import stats
import seaborn as sns
import pandas as pd

from src import get_cpp_result, get_rust_results, get_python_results
from src.analyze_results import get_short_names, get_short_pc_names


result_path = "../results-archive"
data_path = "../data"
significance_alpha = 0.05

data = {"computer": [], "implementation": [], "runtime": []}
short_pc_names = get_short_pc_names()
for pc_name in os.listdir(result_path):
    results = {}
    results_mean = None
    for uc_folder_name in os.listdir(f"{result_path}/{pc_name}/"):
        for test_dir in os.listdir(f"{result_path}/{pc_name}/{uc_folder_name}/"):
            path = f"{result_path}/{pc_name}/{uc_folder_name}/{test_dir}/"
            result = {}  # in mirco sekunden
            result.update(get_cpp_result(path))
            result.update(get_rust_results(path))
            result.update(get_python_results(path))

            path = f"{data_path}/{uc_folder_name}/{uc_folder_name}_{test_dir}.json"
            file = open(path, "r")
            json_data = json.load(file)
            n_cases_per_test = len(json_data)

            for key in result:
                result[key] /= n_cases_per_test

            if results_mean == None:
                results_mean = result
            else:
                results_mean = {key: results_mean.get(key, 0) + result.get(key, 0)
                                for key in set(results_mean) | set(result)}

            for key in result:
                if key in results:
                    results[key].append(result[key])
                else:
                    results[key] = [result[key]]

    short_names = get_short_names()
    for key in short_names:
        data["computer"].extend([short_pc_names[pc_name]] * len(results[key]))
        data["implementation"].extend([key] * len(results[key]))
        data["runtime"].extend(results[key])

    cpp_short_names = {}
    cpp_data = []
    for key in ["FCL distance", "Jolt intersection", "libccd intersection", "Bullet distance"]:
        cpp_short_names[key] = short_names[key]
        cpp_data.append(results[key])

    rust_short_names = {}
    rust_data = []
    for key in ["ncollide_distance", "collision-rs_nasterov_gjk", "collision-rs_distance_gjk",
                "collision-rs_intersect_gjk", "gjk-rs_nasterov_gjk"]:
        rust_short_names[key] = short_names[key]
        rust_data.append(results[key])

    python_short_names = {}
    python_data = []
    for key in ["Pybullet", "distance3d Nesterov (Primitives with acceleration)", "distance3d Nesterov (Primitives)",
                "distance3d Nesterov (with acceleration)", "distance3d Nesterov",
                "distance3d Jolt (distance)", "distance3d Jolt (intersection)", "distance3d Original"]:
        python_short_names[key] = short_names[key]
        python_data.append(results[key])

    #  Mean
    results_mean = {key: results_mean.get(key, 0) / len(results[key])
                    for key in set(results_mean)}

    results_mean = dict(sorted(results_mean.items(), key=lambda item: item[1]))
    print("---", short_pc_names[pc_name], "---")
    print("\n -- Mean: --")
    for key in results_mean:
        print(key, ':', "%.4f µs" % results_mean[key])

    print("\n-- Max Index: --")
    # Longest case per implementation
    for key in short_names:
        i = np.argmax(results[key])
        print(f"{key} : {i}")

    # Normal test
    print(f"\n-- Normal Test --")
    for key in results:
        statistic, p = stats.normaltest(results[key])
        print(f"{short_names[key]}: {p:.2f}")

    def show_data_ds(data, short_names, language):

        print(list(short_names.values()))
        i = 0
        for result_a in data:
            print(list(short_names.values())[i], end='')

            j = 0
            for result_b in data:
                U1, p = scipy.stats.mannwhitneyu(result_a, result_b, alternative="less")
                eff_size = U1 / (len(result_a) * len(result_b))
                if p > significance_alpha:
                    print(" & ns", end='')
                else:
                    print(f" & {eff_size:.2f}", end='')
                j += 1

            print(" \\\\")

            i += 1

    show_data_ds(cpp_data, cpp_short_names, "cpp")
    show_data_ds(rust_data, rust_short_names, "rust")
    show_data_ds(python_data, python_short_names, "python")

data = pd.DataFrame(data)
print(data.groupby("implementation").describe())
#  Violin Plot
fig = plt.figure(figsize=(6, 9))

ax = plt.subplot(111)
sns.violinplot(ax=ax, data=data, x="runtime", y="implementation", hue="computer",
               split=True, inner="quart", density_norm="count", log_scale=True, cut=0)

plt.yticks(np.arange(0, len(short_names.values()), 1.0))
ax.set_yticklabels(short_names.values())
ax.set_xlabel("Time per collision check [µs]")
ax.set_xlim((1e-3, 1e4))
ax.set_ylabel(None)

plt.tick_params(
    axis='x',
    which='both',
    bottom=False,
    top=False,
    labelbottom=True)

fig.tight_layout()
plt.savefig(f"violin.pdf")
#plt.show()



