import json

from distance3d.gjk import gjk


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
            "collider1": collider0.to_dict(),
            "collider2": collider1.to_dict(),
            "distance": distance,
        }
        shapes.append(data)
        i += 1

    file = open(f"{save_path}/{file_name}", "w")
    json.dump(shapes, file, indent=4)
