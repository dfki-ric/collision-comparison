import json
import os
import numpy as np
from matplotlib import pyplot as plt
import scipy
from scipy import stats

from src import get_cpp_result, get_rust_results, get_python_results
from src.analyze_results import get_short_names, get_short_pc_names

# Einheit micro sekunden (µs)

result_path = "../results-archive"
data_path = "../data"
significance_alpha = 0.05

for pc_name in os.listdir(result_path):

    for name in os.listdir(f"{result_path}/{pc_name}/"):

        results = {}
        results_mean = None
        for dir in os.listdir(f"{result_path}/{pc_name}/{name}/"):

            path = f"{result_path}/{pc_name}/{name}/{dir}/"
            result = {}  # in mirco sekunden
            result.update(get_cpp_result(path))
            result.update(get_rust_results(path))
            result.update(get_python_results(path))

            path = f"{data_path}/{name}/{name}_{dir}.json"
            file = open(path, "r")
            json_data = json.load(file)
            case_amount = len(json_data)

            for key in result:
                result[key] /= case_amount

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

        pos = []
        data = []
        i = 0
        short_names = get_short_names()
        for key in short_names:
            pos.append(i)
            data.append(np.array(results[key]))
            i += 1

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

        short_pc_names = get_short_pc_names()


        #  Mean
        results_mean = {key: results_mean.get(key, 0) / len(results[key])
                        for key in set(results_mean)}

        results_mean = dict(sorted(results_mean.items(), key=lambda item: item[1]))
        print("---", name, "on", short_pc_names[pc_name], "---")
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

        #  Violin Plot
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.violinplot(data, pos, points=10000, vert=False, widths=1,
                    showmeans=True, showextrema=True, showmedians=True)

        ax.set_xscale('log')
        plt.yticks(np.arange(0, len(short_names.values()), 1.0))
        ax.set_yticklabels(short_names.values())
        ax.set_xlabel("Time per collision check in µs")
        ax.set_xlim(0.001, 8000)

        plt.tick_params(
            axis='x',
            which='both',
            bottom=False,
            top=False,
            labelbottom=True)

        ax.set_title(f"{name} on {short_pc_names[pc_name]}")
        fig.tight_layout()
        plt.show()
        plt.savefig(f"{name}_on_{short_pc_names[pc_name]}_violin.png")



