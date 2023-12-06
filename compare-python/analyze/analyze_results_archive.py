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
        for key in results_mean:
            i = np.argmax(results[key])
            print(f"{key} : {i}")


        cpp_results = [results["FCL distance"],
                       results["Jolt intersection"],
                       results["libccd intersection"],
                       results["Bullet distance"]]

        rust_results = [results["ncollide_distance"],
                        results["collision-rs_nasterov_gjk"],
                        results["collision-rs_distance_gjk"],
                        results["collision-rs_intersect_gjk"],
                        results["gjk-rs_nasterov_gjk"]]

        python_results = [results["Pybullet"],
                          results["distance3d Nesterov (Primitives with acceleration)"],
                          results["distance3d Nesterov (Primitives)"],
                          results["distance3d Nesterov (with acceleration)"],
                          results["distance3d Nesterov"],
                          results["distance3d Jolt (intersection)"],
                          results["distance3d Jolt (distance)"],
                          results["distance3d Original"]]

        # ANOVA
        print("\n-- ANOVA --")
        print("ANOVA for every case as its own group:")
        F, p = scipy.stats.f_oneway(*results.values())
        print("F: ", F)
        print("p: ", p)

        print("ANOVA for every C/C++ case as its own group:")
        F, p = scipy.stats.f_oneway(*cpp_results)
        print("F: ", F)
        print("p: ", p)

        print("ANOVA for every Rust case as its own group:")
        F, p = scipy.stats.f_oneway(*rust_results)
        print("F: ", F)
        print("p: ", p)

        print("ANOVA for every Python case as its own group:")
        F, p = scipy.stats.f_oneway(*python_results)
        print("F: ", F)
        print("p: ", p)

        # print("ANOVA for all cases from one language as one group:")
        # F, p = scipy.stats.f_oneway(cpp_results, rust_results, python_results)
        # print("F: ", F)
        # print("p: ", p)

        # T test
        print("\n -- T Test --")
        for key_a, result_a in results.items():
            for key_b, result_b in results.items():
                if result_a == result_b:
                    continue

                print(key_a, " vs ", key_b)
                print(result_a)

                statistics, p, df, confidence_interval = scipy.stats.ttest_ind(result_a, result_b)
                print("statistics: ", statistics)
                print("p: ", p)
                print("df: ", df)
                print("confidence_interval: ", confidence_interval)


        #  Violin Plot
        pos = []
        data = []
        i = 0
        short_names = get_short_names()
        for key in short_names:
            pos.append(i)
            data.append(np.array(results[key]))
            i += 1

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.violinplot(data, pos, points=10000, vert=False, widths=1,
                    showmeans=True, showextrema=True, showmedians=True)

        ax.set_xscale('log')
        plt.yticks(np.arange(0, i, 1.0))
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
        plt.savefig(f"{name} on {pc_name}.png")



