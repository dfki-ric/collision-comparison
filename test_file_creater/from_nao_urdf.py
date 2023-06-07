import json
import os
import numpy as np
from distance3d.broad_phase import BoundingVolumeHierarchy
from distance3d.gjk import gjk
from pytransform3d.urdf import UrdfTransformManager

data_path = "../data/"
urdf_file = "urdfs/nao_robot/nao_description/urdf/naoV40_generated_urdf/nao.urdf"
urdf_working_dir = "urdfs/"

shapes = []

isExist = os.path.exists(data_path)
if not isExist:
   os.makedirs(data_path)

tm = UrdfTransformManager()
f = open(data_path + urdf_file, "r")
urdf = f.read()
tm.load_urdf(urdf, package_dir=data_path + urdf_working_dir)

bvh = BoundingVolumeHierarchy(tm, "NaoH25V40")
bvh.fill_tree_with_colliders(tm,  make_artists=True)

cases = bvh.aabb_overlapping_with_self()

i = 0
for case in cases:
    print("Case: ", i)

    collider0 = case[0][1]
    collider1 = case[1][1]

    distance, _, _, _ = gjk(collider0, collider1)
    data = {
        "case": i,
        "collider1": collider0.to_dict(),
        "collider2": collider1.to_dict(),
        "distance": distance,
    }
    shapes.append(data)
    i += 1

file = open(f"{data_path}nao_test_cases.json", "w")
json.dump(shapes, file, indent=4)




