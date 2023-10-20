import matplotlib.pyplot as plt
import numpy as np

from distance3d.gjk import gjk


def analyze_robot(bvh):
    colliders = bvh.get_colliders()

    collider_count = get_collider_count(colliders)
    distances, average_dist = get_distances_all(colliders)
    sizes = get_collider_sizes(colliders)
    average_size = get_average_size(sizes)

    after_broad_phase_with_self = bvh.aabb_overlapping_with_self()
    collider_after_broad = get_colliders_from_pairs(after_broad_phase_with_self)
    collider_count_after_broad = get_collider_count(collider_after_broad)

    distances_after_broad, average_dist_after_broad = get_distances_cases(after_broad_phase_with_self)
    sizes_after_broad = get_collider_sizes(collider_after_broad)
    average_size_after_broad = get_average_size(sizes_after_broad)

    print("---- Without Broad Phase ----")
    print("Colliders: ", len(colliders))

    print_collider_distribution(collider_count)

    print("Average Size: ", average_size)

    print("Collision Cases: ", (len(colliders) * len(colliders)) - len(colliders))
    print("Average Distance: ", average_dist)
    plot_distance_distribution(distances, "Distance Distribution")

    print("---- With Broad Phase ----")
    print("Colliders: ", len(collider_after_broad))

    print_collider_distribution(collider_count)

    print("Average Size: ", average_size_after_broad)

    print("Collision Cases: ", len(after_broad_phase_with_self))
    print("Average Distance: ", average_dist_after_broad)
    ## plot_distance_distribution(distances_after_broad, "Distance Distribution after broad phase")


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


def get_distances_all(colliders):

    distances = []
    dist_sum = 0
    counter = 0

    for (i, collider0) in enumerate(colliders):
        for (j, collider1) in enumerate(colliders):
            if collider0 == collider1:
                continue

            distance, _, _, _ = gjk(collider0, collider1)
            distances.append(distance)

            dist_sum += distance
            counter += 1

    return distances, dist_sum / counter


def get_distances_cases(pairs):

    distances = []
    dist_sum = 0
    counter = 0

    for pair in pairs:
        collider0 = pair[0][1]
        collider1 = pair[0][1]

        distance, _, _, _ = gjk(collider0, collider1)
        distances.append(distance)

        dist_sum += distance
        counter += 1

    return distances, dist_sum / counter


def get_colliders_from_pairs(pairs):
    colliders = []
    names = []

    for pair in pairs:

        name0 = pair[0][0]
        name1 = pair[1][0]
        collider0 = pair[0][1]
        collider1 = pair[0][1]

        collider0_found = False
        collider1_found = False
        for name in names:
            if name0 == name:
                collider0_found = True

            if name1 == name:
                collider1_found = True

            if collider0_found and collider1_found:
                break

        if not collider0_found:
            names.append(name0)
            colliders.append(collider0)

        if not collider1_found:
            names.append(name1)
            colliders.append(collider1)

    return colliders


def get_collider_sizes(colliders):
    size = []

    for collider in colliders:
        aabb = collider.aabb()
        size.append(np.linalg.norm(aabb[:, 1] - aabb[:, 0]))

    return size


def get_average_size(sizes):
    size_sum = 0
    for size in sizes:
        size_sum += size

    return size_sum / len(sizes)


def plot_distance_distribution(distances, label):

    step = 0.02
    max_dist = 0.1
    for distance in distances:
        if distance > max_dist:
            max_dist = distance

    counter = np.zeros([int(max_dist / step) + 1])
    for distance in distances:
        index = int(distance / step)
        counter[index] += 1

    import decimal
    def drange(x, y, jump):
        while x < y:
            yield float(x)
            x += decimal.Decimal(jump)

    x = list(drange(0, max_dist, step))

    plt.plot(x, counter, linewidth=2.0)
    plt.title = label
    plt.yticks([])
    plt.xlabel("Distance in m")
    plt.ylabel("Relative Frequency")

    plt.show()


def print_collider_distribution(colliders):
    collider_sum = 0

    for name in colliders:
        collider_sum += colliders[name]

    print("Collider Type Distribution:")
    for name in colliders:
        if colliders[name] == 0:
            continue

        print("  ", name, ":", int((colliders[name] / collider_sum) * 100), "%")

