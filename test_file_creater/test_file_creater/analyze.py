from distance3d.gjk import gjk


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


def get_average_dist(colliders):
    dist_sum = 0
    i = 0
    for collider0 in colliders:
        for collider1 in colliders:
            if collider0 == collider1:
                continue

            distance, _, _, _ = gjk(collider0, collider1)
            dist_sum += distance
            i += 1

    return dist_sum / i


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