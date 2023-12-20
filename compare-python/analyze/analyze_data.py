
import json
import os

import pandas as pd
from matplotlib import pyplot as plt

from src import get_cpp_result, get_rust_results, get_python_results

# Einheit micro sekunden (µs)


data_path = "../data"

for name in os.listdir(data_path):
    if name == "urdfs" or name == "current.json" or ".zip" in name:
        continue

    print(name)

    case_ammount_sum = 0
    case_ammount_counter = 0
    case_ammounts = []
    colliding_case = 0
    dist_sum = 0

    for file_name in os.listdir(f"{data_path}/{name}"):
        path = f"{data_path}/{name}/{file_name}"
        file = open(path, "r")
        json_data = json.load(file)
        case_amount = len(json_data)

        case_ammount_sum += case_amount
        case_ammount_counter += 1
        case_ammounts.append(case_amount)

        for case in json_data:
            if case["distance"] <= 0:
                colliding_case += 1
            else:
                dist_sum += case["distance"]


    average_case_ammount = case_ammount_sum / case_ammount_counter
    print(f"average case ammount: {average_case_ammount:.2f}")

    colliding_case_percent = (colliding_case / case_ammount_sum) * 100
    print(f"colliding case percent: {colliding_case_percent:.2f}%")

    mean_distance = dist_sum / (case_ammount_sum - colliding_case)
    print(f"mean distance of not colliding: {mean_distance:.2f}")

    ax = pd.Series(case_ammounts).plot(kind='density')
    ax.set_title(name)
    ax.set_xlabel("Checks per case")
    ax.set_xlim(left=0, right=100)
    ax.set_ylim(bottom=0, top=0.2)
   # ax.yaxis.set_tick_params(labelleft=False)
    plt.show()







