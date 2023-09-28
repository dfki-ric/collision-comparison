import json
import os


# Einheit micro sekunden

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
results = []
results_sum = None

for dir in os.listdir(result_path):

    path = f"{result_path}/{dir}/"
    result = {}  # in mirco sekunden
    result.update(get_cpp_result(path))
    result.update(get_rust_results(path))
    result.update(get_python_results(path))

    if results_sum == None:
        results_sum = result
    else:
        results_sum = {key: results_sum.get(key, 0) + result.get(key, 0)
                       for key in set(results_sum) | set(result)}

    results.append(result)

results_sum = {key: results_sum.get(key, 0) / len(results)
               for key in set(results_sum)}


results_sum = dict(sorted(results_sum.items(), key=lambda item: item[1]))
for key in results_sum:
    print(key, ':', "%.4f" % results_sum[key])
