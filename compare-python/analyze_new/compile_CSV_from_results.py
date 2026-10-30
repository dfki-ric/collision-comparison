import argparse
import datetime
import json
import os
import sys
import warnings
from pathlib import Path

import pandas as pd

def get_cpp_result(path):
    try:
        with open(Path(path, "cpp_result.json")) as f:
            result = json.load(f)  # in seconds
    except FileNotFoundError:
        warnings.warn(f"No C++ results found under {path}")
        return {}

    data = {}
    for r in result["results"]:
        name = r["name"]
        median = r["median(elapsed)"] * 1000000
        data[f"{name}"] = median

    return data


def get_python_results(path):
    data = {}

    try:
        with open(Path(path, "distance3d_result.json")) as f:
            distance3d_result = json.load(f)

            for name in distance3d_result:
                median = distance3d_result[name]
                data[f"distance3d {name}"] = median
    except FileNotFoundError:
        warnings.warn(f"No python[distance3d] results found under {path}")

    try:
        with open(Path(path, "pybullet_result.json")) as f:
            pybullet_result = json.load(f)

            for name in pybullet_result:
                median = pybullet_result[name]
                data[f"{name}"] = median
    except FileNotFoundError:
        warnings.warn(f"No python[pybullet] results found under {path}")

    return data


def get_rust_results(path):
    data = {}

    path = Path(path, "criterion")
    if not os.path.exists(path):
        warnings.warn(f"No rust results found under {path}")
        return {}
    for dir in os.listdir(path):
        if dir == "report":
            continue

        try:
            with open(f"{path}/{dir}/new/estimates.json") as f:
                result = json.load(f)  # in ns
        except FileNotFoundError:
            warnings.warn(f"No rust results found under {path}")
            return {}

        median = result["mean"]["point_estimate"] / 1000
        data[f"{dir}"] = median

    return data

RESULT_PATH = "../results-archive"
DATA_PATH = "../data"



def compile_results(path_to_result_dir: Path, path_to_case_files: Path):
    dataframe_records = []
    for result_file in os.listdir(path_to_result_dir):
        # fetch the results for all algorithms for the current file
        file_result_path = Path(path_to_result_dir, result_file)
        result = {}  # in microseconds
        result.update(get_cpp_result(file_result_path))
        result.update(get_rust_results(file_result_path))
        result.update(get_python_results(file_result_path))

        # open the corresponding case file to count how many cases were in it:
        path_to_case_file = Path(path_to_case_files, f"{path_to_case_files.name}_{result_file}.json")
        with open(path_to_case_file, "r") as f:
            json_data = json.load(f)
            n_cases_per_test = len(json_data)

        # compute mean time per case for all algorithms:
        for key in result:
            result[key] /= n_cases_per_test

        dataframe_records.append({
            "file": int(result_file),
            **result
        })

    if len(dataframe_records) == 0:
        print("No results to save")
        exit(1)
    # store into a CSV:
    df = pd.DataFrame.from_records(dataframe_records)
    df.sort_values(by="file", ascending=True, inplace=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_filename = f"{path_to_case_files.name}_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)

    print(f"Saved {len(dataframe_records)} records to {csv_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('results_path', default=None,
                        help='Directory in which the results are saved. Is expected to contain folders named 0,1,2,... for every case file.')
    parser.add_argument('case_file_path', default=None,
                        help='Directory in which the case files live. Is expected to contain files called {name_of_dir}_[0,1,2,...].json for every case file.')
    args = parser.parse_args()

    if args.results_path is None or args.case_file_path is None:
        parser.print_help()
        exit(1)

    compile_results(Path(args.results_path), Path(args.case_file_path))