import json
import os


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


def get_short_names():
    return {
        "FCL distance": "HPP-FCL",
        "Jolt intersection": "Jolt",
        "libccd intersection": "libccd",
        "Bullet distance": "Bullet",

        "ncollide_distance": "ncollide",
        "collision-rs_nasterov_gjk": "collision-rs 3",
        "collision-rs_distance_gjk": "collision-rs 2",
        "collision-rs_intersect_gjk": "collision-rs 1",

        "gjk-rs_nasterov_gjk": "gjk-rs",
        "Pybullet": "pybullet",

        "distance3d Nesterov (Primitives with acceleration)": "distance3d 7",
        "distance3d Nesterov (Primitives)": "distance3d 6",
        "distance3d Nesterov (with acceleration)": "distance3d 5",
        "distance3d Nesterov": "distance3d 4",
        "distance3d Jolt (intersection)": "distance3d 2",
        "distance3d Jolt (distance)": "distance3d 3",
        "distance3d Original": "distance3d 1",
    }