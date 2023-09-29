import json

import numpy as np

from distance3d.colliders import Sphere, Box, Capsule, Cylinder
from distance3d.gjk import gjk


def to_dict(collider):
    type = collider.__class__.__name__
    data = {
        "type": type,
        "collider2origin": collider.collider2origin().tolist()
    }

    if type == Sphere:
        data += {
            "radius": collider.radius
        }
    if type == Box:
        data += {
            "size": collider.size.tolist()
        }
    if type == Capsule or type == Cylinder:
        data += {
            "radius": collider.radius,
            "height": collider.height
        }

    return data


def from_dict(data):
    if data["type"] == "Sphere":
        return Sphere(np.array(data["collider2origin"])[:3, 3], data["radius"])
    if data["type"] == "Box":
        return Box(np.array(data["collider2origin"]), np.array(data["size"]))
    if data["type"] == "Capsule":
        return Capsule(np.array(data["collider2origin"]), data["radius"], data["height"])
    if data["type"] == "Cylinder":
        return Cylinder(np.array(data["collider2origin"]), data["radius"], data["height"])


def write_test_file(cases, save_path, file_name):
    shapes = []

    i = 0
    for case in cases:
        print("Case: ", i)

        collider0 = case[0][1]
        collider1 = case[1][1]

        distance, _, _, _ = gjk(collider0, collider1)
        data = {
            "case": i,
            "collider1": to_dict(collider0),
            "collider2": to_dict(collider1),
            "distance": distance,
        }
        shapes.append(data)
        i += 1

    file = open(f"{save_path}/{file_name}", "w")
    json.dump(shapes, file, indent=4)


def load_test_file(path):
    file = open(path)
    data = json.load(file)

    colliders = []
    for case in data:
        colliders.append([from_dict(case["collider1"]), from_dict(case["collider2"])])

    return colliders
