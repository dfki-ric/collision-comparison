import json
import os

import pandas as pd
from matplotlib import pyplot as plt

from src import get_cpp_result, get_rust_results, get_python_results

# Einheit micro sekunden (µs)

result_path = "../results"
data_path = "../data"
name = "uc1_ur10_collision"
results = {}
results_sum = None

for dir in os.listdir(result_path):

    path = f"{result_path}/{dir}/"
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

results_sum = {key: results_sum.get(key, 0) / len(results[key])
               for key in set(results_sum)}




results_sum = dict(sorted(results_sum.items(), key=lambda item: item[1]))
for key in results_sum:
    print(key, ':', "%.4f µs" % results_sum[key])

for key in results:
    ax = pd.Series(results[key]).plot(kind='density')
    ax.set_title(key)
    ax.set_xlabel("Time per case in µs")
    ax.set_xlim(left=0)
    ax.yaxis.set_tick_params(labelleft=False)
    plt.show()
    plt.savefig(f"{key}.png")
