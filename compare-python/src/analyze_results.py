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


def get_short_name(name):
    short_names = {
        "FCL distance": "hpp-fcl",
        "Jolt intersection": "Jolt",
        "libccd intersection": "libccd",
        "Bullet distance": "Bullet",

        "ncollide_distance": "ncollide",
        "collision-rs_intersect_gjk": "col-rs: inter",
        "collision-rs_distance_gjk":  "col-rs: dist",
        "collision-rs_nasterov_gjk":  "col-rs: nes",

        "gjk-rs_nasterov_gjk": "gjk-rs: nes",
        "Pybullet": "pybullet",

        "distance3d Nesterov (Primitives with acceleration)": "dis3d: nes acc full-jit",
        "distance3d Nesterov (Primitives)": "dis3d: nes full-jit",
        "distance3d Nesterov (with acceleration)": "dis3d: nes acc part-jit",
        "distance3d Nesterov": "dis3d: nes part-jit",
        "distance3d Jolt (intersection)": "dis3d: Jolt inter",
        "distance3d Jolt (distance)": "dis3d: Jolt dist",
        "distance3d Original": "dis3d: org-gjk",
    }

    return short_names[name]