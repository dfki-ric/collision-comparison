import numpy as np
from distance3d import colliders, random
from distance3d.gjk._gjk_nesterov_accelerated import gjk_nesterov_accelerated

iterations = 100
random_state = np.random.RandomState(84)
shape_names = ["sphere", "capsule", "cylinder"]

original_iteration_sum = 0
jolt_iteration_sum = 0
nasterov_iteration_sum = 0

for i in range(iterations):


    shape1 = shape_names[random_state.randint(len(shape_names))]
    args1 = random.RANDOM_GENERATORS[shape1](random_state)
    shape2 = shape_names[random_state.randint(len(shape_names))]
    args2 = random.RANDOM_GENERATORS[shape2](random_state)
    collider1 = colliders.COLLIDERS[shape1](*args1)
    collider2 = colliders.COLLIDERS[shape2](*args2)

    collider1.round_values(6)
    collider2.round_values(6)

    nasterov_iterations = gjk_nesterov_accelerated(collider1, collider2)[3]
    print("Nasterov Intertions", nasterov_iterations)