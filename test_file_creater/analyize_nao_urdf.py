from distance3d.colliders import COLLIDERS
from test_file_creater.load_nao import get_nao_bvh

data_path = "../data/"
bvh = get_nao_bvh(data_path)

colliders = bvh.get_colliders()

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


after_broard_phase_with_self = bvh.aabb_overlapping_with_self()


print("Done")

