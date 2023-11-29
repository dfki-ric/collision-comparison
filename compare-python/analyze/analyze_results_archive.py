import json
import os
import numpy as np
from matplotlib import pyplot as plt

from src import get_cpp_result, get_rust_results, get_python_results
from src.analyze_results import get_short_names

# Einheit micro sekunden (µs)



result_path = "../results-archive"
data_path = "../data"

for pc_name in os.listdir(result_path):

    for name in os.listdir(f"{result_path}/{pc_name}/"):

        results = {}
        results_sum = None
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

            if results_sum == None:
                results_sum = result
            else:
                results_sum = {key: results_sum.get(key, 0) + result.get(key, 0)
                               for key in set(results_sum) | set(result)}

            for key in result:

                if key in results:
                    results[key].append(result[key])
                else:
                    results[key] = [result[key]]

        #  Mean
        results_sum = {key: results_sum.get(key, 0) / len(results[key])
                       for key in set(results_sum)}

        results_sum = dict(sorted(results_sum.items(), key=lambda item: item[1]))
        print("---", name, "---")
        print("Mean:")
        for key in results_sum:
            print(key, ':', "%.4f µs" % results_sum[key])

        print("Max Index:")
        # Longest case per implementation
        for key in results_sum:
            i = np.argmax(results[key])
            print(f"{key} : {i}")



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
