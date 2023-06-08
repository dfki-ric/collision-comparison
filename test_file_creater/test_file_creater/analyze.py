import numpy as np
from distance3d.gjk import gjk
import matplotlib.pyplot as plt


def get_collider_count(colliders):
    collider_count = {
        "ConvexHullVertices": 0,
        "Box": 0,
        "Mesh": 0,
        "Sphere": 0,
        "Capsule": 0,
        "Ellipsoid": 0,
        "Cylinder": 0,
        "Disk": 0,
        "Ellipse": 0,
        "Cone": 0,
    }

    for collider in colliders:
        collider_data = collider.to_dict()
        for collider_name in collider_count:
            if collider_data["type"] == collider_name:
                collider_count[collider_name] += 1
                break

    return collider_count


def get_distances(colliders):

    distances = np.zeros([len(colliders), len(colliders)])
    dist_sum = 0
    counter = 0

    for (i, collider0) in enumerate(colliders):
        for (j, collider1) in enumerate(colliders):
            if collider0 == collider1:
                continue

            distance, _, _, _ = gjk(collider0, collider1)
            distances[i, j] = distance

            dist_sum += distance
            counter += 1

    return distances, dist_sum / counter


def get_colliders_from_pairs(pairs):
    colliders = []

    for pair in pairs:
        collider0 = pair[0][1]
        collider1 = pair[0][1]

        collider0_found = False
        collider1_found = False
        for collider in colliders:
            if collider0 == collider:
                collider0_found = True

            if collider0 == collider:
                collider0_found = True

            if collider0_found and collider1_found:
                break

        if not collider0_found:
            colliders.append(collider0)

        if not collider1_found:
            colliders.append(collider1)

    return colliders


def plot_distance_distribution(distances, label):

    step = 0.02
    max_dist = 0.0
    for distance in distances.flatten():
        if distance > max_dist:
            max_dist = distance

    counter = np.zeros([int(max_dist / step) + 1])
    for distance in distances.flatten():
        index = int(distance / step)
        counter[index] += 1

    import decimal
    def drange(x, y, jump):
        while x < y:
            yield float(x)
            x += decimal.Decimal(jump)

    x = list(drange(0, max_dist, step))

    # plot
    fig, ax = plt.subplots()

    ax.plot(x[1:], counter[1:], linewidth=2.0, label=label)


    plt.show()


def print_collider_distribution(colliders):
    collider_sum = 0

    for name in colliders:
        collider_sum += colliders[name]

    for name in colliders:
        if colliders[name] == 0:
            continue

        print(name, ":", int((colliders[name] / collider_sum) * 100), "%")
