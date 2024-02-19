import json
import warnings
import os


def get_cpp_result(path):
    try:
        with open(f"{path}/cpp_result.json") as f:
            result = json.load(f)  # in seconds
    except FileNotFoundError:
        warnings.warn(f"No results found under {path}")
        return {}

    data = {}
    for r in result["results"]:
        name = r["name"]
        median = r["median(elapsed)"] * 1000000
        data[f"{name}"] = median

    return data


def get_python_results(path):
    try:
        with open(f"{path}/distance3d_result.json") as f:
            distance3d_result = json.load(f)
    except FileNotFoundError:
        warnings.warn(f"No results found under {path}")
        return {}

    data = {}
    for name in distance3d_result:
        median = distance3d_result[name]
        data[f"distance3d {name}"] = median

    try:
        with open(f"{path}/pybullet_result.json") as f:
            pybullet_result = json.load(f)
    except FileNotFoundError:
        warnings.warn(f"No results found under {path}")
        return {}

    for name in pybullet_result:
        median = pybullet_result[name]
        data[f"{name}"] = median

    return data


def get_rust_results(path):
    data = {}

    path = f"{path}criterion"
    if not os.path.exists(path):
        warnings.warn(f"No results found under {path}")
        return {}
    for dir in os.listdir(path):
        if dir == "report":
            continue

        try:
            with open(f"{path}/{dir}/new/estimates.json") as f:
                result = json.load(f)  # in ns
        except FileNotFoundError:
            warnings.warn(f"No results found under {path}")
            return {}

        median = result["mean"]["point_estimate"] / 1000
        data[f"{dir}"] = median

    return data


def get_short_names():
    return {
        "FCL distance": "HPP-FCL",
        "Jolt intersection": "Jolt",
        "libccd intersection": "libccd",
        "Bullet distance": "Bullet",

        "ncollide_distance": "ncollide",
        "collision-rs_nasterov_gjk": "collision-rs nest",
        "collision-rs_distance_gjk": "collision-rs dist",
        "collision-rs_intersect_gjk": "collision-rs inter",

        "gjk-rs_nasterov_gjk": "gjk-rs",
        "Pybullet": "pybullet",

        "distance3d Nesterov (Primitives with acceleration)": "distance3d tuple acc",
        "distance3d Nesterov (Primitives)": "distance3d tuple no acc",
        "distance3d Nesterov (with acceleration)": "distance3d nest acc",
        "distance3d Nesterov": "distance3d nest no acc",
        "distance3d Jolt (intersection)": "distance3d jolt inter",
        "distance3d Jolt (distance)": "distance3d jolt dist",
        "distance3d Original": "distance3d org",
    }

def get_short_pc_names():
    return {
        "UPLINX-4-U": "PC1",
        "TEAM7-STUD-1B-U": "PC2",
        "Alexanders-PC": "PC3",
        "JoltTest": "PC4",
        "UPLINX-3-U": "PC5",
    }