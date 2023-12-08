import json
import os
import numpy as np
from matplotlib import pyplot as plt
import scipy

from src import get_cpp_result, get_rust_results, get_python_results
from src.analyze_results import get_short_names

# Einheit micro sekunden (µs)

result_path = "../results-archive"
data_path = "../data"

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
                    "distance3d Nesterov (with acceleration)", "distance3d Nesterov", "distance3d Jolt (intersection)",
                    "distance3d Jolt (distance)", "distance3d Original"]:
            python_short_names[key] = short_names[key]
            python_data.append(results[key])

        #  Mean
        results_mean = {key: results_mean.get(key, 0) / len(results[key])
                        for key in set(results_mean)}

        results_mean = dict(sorted(results_mean.items(), key=lambda item: item[1]))
        print("---", name, "on", pc_name, "---")
        print("\n -- Mean: --")
        for key in results_mean:
            print(key, ':', "%.4f µs" % results_mean[key])

        print("\n-- Max Index: --")
        # Longest case per implementation
        for key in short_names:
            i = np.argmax(results[key])
            print(f"{key} : {i}")

        # ANOVA
        print("\n-- ANOVA --")
        print("ANOVA for every case as its own group:")
        F, p = scipy.stats.f_oneway(*results.values())
        print("F: ", F)
        print("p: ", p)

        print("ANOVA for every C/C++ case as its own group:")
        F, p = scipy.stats.f_oneway(*cpp_data)
        print("F: ", F)
        print("p: ", p)

        print("ANOVA for every Rust case as its own group:")
        F, p = scipy.stats.f_oneway(*rust_data)
        print("F: ", F)
        print("p: ", p)

        print("ANOVA for every Python case as its own group:")
        F, p = scipy.stats.f_oneway(*python_data)
        print("F: ", F)
        print("p: ", p)

        # print("ANOVA for all cases from one language as one group:")
        # F, p = scipy.stats.f_oneway(cpp_results, rust_results, python_results)
        # print("F: ", F)
        # print("p: ", p)

        # T test
        # print("\n -- T Test --")

        def show_data_ds(data, short_names, language):
            d_results = []
            i = 0
            for result_a in data:
                d_results.append([])

                for result_b in data:
                    statistics, _ = scipy.stats.ttest_ind(result_a, result_b)
                    d = abs(statistics * np.sqrt((1 / len(result_a)) + (1 / len(result_b))))

                    if d <= 0.3:
                        d = 0.2
                    elif d <= 0.6:
                        d = 0.5
                    elif d <= 0.9:
                        d = 0.8
                    elif d > 0.9:
                        d = 1.0

                    d_results[i].append(d)

                i += 1

            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)

            plt.imshow(d_results)
            ax.set_title(f"{name} on {pc_name}")
            ax.set_aspect('equal')

            plt.xticks(np.arange(0, len(short_names.values()), 1.0))
            plt.yticks(np.arange(0, len(short_names.values()), 1.0))
            ax.set_xticklabels(short_names.values())
            ax.set_yticklabels(short_names.values())
            plt.xticks(rotation=90, ha='right')

            cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
            cax.get_xaxis().set_visible(False)
            cax.get_yaxis().set_visible(False)
            cax.patch.set_alpha(0)
            cax.set_frame_on(False)
            plt.colorbar(orientation='vertical')

            fig.tight_layout()
            plt.show()
            plt.savefig(f"{name}_on_{pc_name}_d_{language}.png")


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

        ax.set_title(f"{name} on {pc_name}")
        fig.tight_layout()
        plt.show()
        plt.savefig(f"{name}_on_{pc_name}_violin.png")



