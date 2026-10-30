import argparse
import datetime
import json
import os
import socket
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

        estimates_path = Path(path, dir, "new", "estimates.json")
        if not estimates_path.exists():
            # benchmark groups (used for flat sampling) are stored in target/criterion/<name>/all_cases
            estimates_path = Path(path, dir, "all_cases", "new", "estimates.json")
        try:
            with open(estimates_path) as f:
                result = json.load(f)  # in ns
        except FileNotFoundError:
            # e.g., the benchmark crashed: skip only this algorithm, keep the results of the others
            warnings.warn(f"No rust results found under {path}/{dir}")
            continue

        median = result["median"]["point_estimate"] / 1000
        data[f"{dir}"] = median

    return data

RESULT_PATH = "../results-archive"
DATA_PATH = "../data"



def count_mesh_faces(mesh_path: Path, cache: dict):
    """Number of faces in an OBJ file (cached, the same meshes are used in many case files)."""
    if mesh_path not in cache:
        with open(mesh_path) as f:
            cache[mesh_path] = sum(1 for line in f if line.startswith("f "))
    return cache[mesh_path]


def load_target_distances(path_to_case_files: Path):
    """Target distances of the distance sweep (target_distances.csv next to the case files), if there are any."""
    path = Path(path_to_case_files, "target_distances.csv")
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    return dict(zip(df["file_name"], df["target_distance"]))


def get_case_file_info(path_to_case_files: Path, file_index: int, mesh_face_counts: dict, target_distances: dict):
    """Information about a case file that the analysis needs in addition to the runtimes.

    - n_checks: number of collision checks (pairs of colliders) in the case file
    - only for case files with a single collision check (the icosphere sweeps):
      - reference_distance: distance computed when the case file was generated
      - n_faces: number of faces of the first collider, if it is a mesh
    - target_distance: target distance of the distance sweep (from target_distances.csv)
    """
    case_file_name = f"{path_to_case_files.name}_{file_index}.json"
    with open(Path(path_to_case_files, case_file_name)) as f:
        cases = json.load(f)

    info = {"n_checks": len(cases)}
    if len(cases) == 1:
        info["reference_distance"] = cases[0]["distance"]
        collider = cases[0]["collider1"]
        if "mesh_path" in collider:
            # mesh paths are relative to the data directory, i.e., to the parent of the case file directory
            mesh_path = Path(path_to_case_files.parent, collider["mesh_path"])
            info["n_faces"] = count_mesh_faces(mesh_path, mesh_face_counts)
    if case_file_name in target_distances:
        info["target_distance"] = target_distances[case_file_name]
    return info


def compile_results(path_to_result_dir: Path, path_to_case_files: Path, computer: str):
    mesh_face_counts = {}
    target_distances = load_target_distances(path_to_case_files)

    dataframe_records = []
    for result_file in os.listdir(path_to_result_dir):
        if not result_file.isdigit():
            # e.g., "<n>.partial" of an interrupted case file (see scripts/benchmarks/benchmark_dataset.sh)
            continue
        # fetch the results for all algorithms for the current file
        file_result_path = Path(path_to_result_dir, result_file)
        # time for all collision checks of the case file in microseconds
        # (not divided by the number of checks: a case file corresponds to one robot configuration)
        result = {}
        result.update(get_cpp_result(file_result_path))
        result.update(get_rust_results(file_result_path))
        result.update(get_python_results(file_result_path))

        dataframe_records.append({
            "file": int(result_file),
            "computer": computer,
            **get_case_file_info(path_to_case_files, int(result_file), mesh_face_counts, target_distances),
            **result
        })

    if len(dataframe_records) == 0:
        print("No results to save")
        exit(1)
    # store into a CSV:
    df = pd.DataFrame.from_records(dataframe_records)
    df.sort_values(by="file", ascending=True, inplace=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    computer_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in computer)
    csv_filename = f"{path_to_case_files.name}_{computer_name}_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)

    print(f"Saved {len(dataframe_records)} records to {csv_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('results_path', default=None,
                        help='Directory in which the results are saved. Is expected to contain folders named 0,1,2,... for every case file.')
    parser.add_argument('case_file_path', default=None,
                        help='Directory in which the case files live. Is expected to contain files called {name_of_dir}_[0,1,2,...].json for every case file.')
    parser.add_argument('--computer', default=os.environ.get("BENCHMARK_COMPUTER", socket.gethostname()),
                        help='Name of the computer on which the benchmark ran (default: environment variable '
                             'BENCHMARK_COMPUTER, otherwise the host name). Stored in the column "computer" and in the file name.')
    args = parser.parse_args()

    if args.results_path is None or args.case_file_path is None:
        parser.print_help()
        exit(1)

    compile_results(Path(args.results_path), Path(args.case_file_path), args.computer)