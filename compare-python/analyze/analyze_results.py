import json
import os

import pandas as pd
from matplotlib import pyplot as plt


# Einheit micro sekunden (µs)

def get_cpp_result(path):
    f = open(f"{path}/cpp_result.json")
    result = json.load(f)  # in sekunden

    data = {}
    for r in result["results"]:
        name = r["name"]
        median = r["median(elapsed)"] * 1000000
        data[f"{name}"] = median

    return data


def get_python_results(path):
    f = open(f"{path}/distance3d_result.json")
    distance3d_result = json.load(f)

    data = {}
    for name in distance3d_result:
        median = distance3d_result[name]
        data[f"distance3d {name}"] = median

    f = open(f"{path}/pybullet_result.json")
    pybullet_result = json.load(f)

    for name in pybullet_result:
        median = pybullet_result[name]
        data[f"{name}"] = median

    return data


def get_rust_results(path):
    data = {}

    path = f"{path}criterion"
    for dir in os.listdir(path):
        if dir == "report":
            continue

        f = open(f"{path}/{dir}/new/estimates.json")
        result = json.load(f)  # in ns

        median = result["mean"]["point_estimate"] / 1000
        data[f"{dir}"] = median

    return data


result_path = "../results"
data_path = "../data"
results = {}
results_sum = None

for dir in os.listdir(result_path):

    path = f"{result_path}/{dir}/"
    result = {}  # in mirco sekunden
    result.update(get_cpp_result(path))
    result.update(get_rust_results(path))
    result.update(get_python_results(path))

    path = f"{data_path}/uc6_ur10_collision_{dir}.json"
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
