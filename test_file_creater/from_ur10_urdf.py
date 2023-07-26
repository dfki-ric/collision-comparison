import json
from distance3d.gjk import gjk
from test_file_creater.load_ur10 import get_u10_bvh

tm, bvh = get_u10_bvh()
cases = bvh.aabb_overlapping_with_self()

shapes = []

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

file = open("../data/ur10_test_cases.json", "w")
json.dump(shapes, file, indent=4)




