import json
import os
import numpy as np
from distance3d import colliders, random
from distance3d.gjk import gjk, gjk_nesterov_accelerated_distance

iterations = 100
shapes = []
random_state = np.random.RandomState(84)
shape_names = ["sphere", "capsule", "cylinder"]

for i in range(iterations):
    print("Interation:", i)

    shape1 = shape_names[random_state.randint(len(shape_names))]
    args1 = random.RANDOM_GENERATORS[shape1](random_state)
    shape2 = shape_names[random_state.randint(len(shape_names))]
    args2 = random.RANDOM_GENERATORS[shape2](random_state)
    collider1 = colliders.COLLIDERS[shape1](*args1)
    collider2 = colliders.COLLIDERS[shape2](*args2)

    collider1.round_values(6)
    collider2.round_values(6)

    distance = gjk_nesterov_accelerated_distance(collider1, collider2)

    data = {
        "collider1": collider1.to_dict(),
        "collider2": collider2.to_dict(),
        "distance": distance,
    }
    shapes.append(data)


path = "../data/"
isExist = os.path.exists(path)
if not isExist:
   os.makedirs(path)

file = open(f"{path}test_data.json", "w")
json.dump(shapes, file, indent=4)




