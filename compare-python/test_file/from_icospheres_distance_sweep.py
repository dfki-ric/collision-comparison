"""
Generate benchmark cases to replicate the experimental setup used in the
paper which introduced Nesterov Accelerated GJK:
"""

import os
import random

import numpy as np
from scipy.spatial.transform import Rotation
import open3d as o3d

from distance3d.colliders import MeshGraph
from distance3d.hydroelastic_contact._tetra_mesh_creation import make_triangular_icosphere
from distance3d.gjk import gjk_distance_original
from distance3d.epa import epa
from src import write_test_file


# Set icosphere details to closely resemble the objects used in the complex_env_dual_arm_collision benchmark
FACE_COUNT = 2885
ICOSPHERE_RADIUS = 0.0946

# Number of random relative poses per target distance:
NUM_POSES_PER_DISTANCE = 100

# Signed separation distances to use, with roughly logarithmic spacing:
TARGET_DISTANCES = np.concatenate([
    -np.array([0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001]),
    [0.0],
    np.array([0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]),
])

subdirectory_name = "../data/icospheres_fixed_size_distance_sweep"
os.makedirs(subdirectory_name + "/meshes", exist_ok=True)

# To get reproducible benchmark cases, set the rng seed:
random.seed(42)
rng = np.random.default_rng(42)


def rand_unit_vector():
    """
    Generate a 3D unit vector pointing in a random direction
    :return: The vector as numpy array
    """
    theta = rng.uniform(0, 2 * np.pi)
    y = rng.uniform(-1, 1)
    k = np.sqrt(1 - y * y)
    return np.array([k * np.cos(theta), k * np.sin(theta), y])


def build_fixed_icosphere(face_count, radius):
    """
    Build a single icosphere mesh with `face_count` faces and the given radius.
    """
    subdivs_needed = np.ceil(np.emath.logn(4, max(face_count, 20) / 20.0)).astype(int)
    source_icosphere = make_triangular_icosphere(center=np.array([0, 0, 0]), radius=radius, order=subdivs_needed)

    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(source_icosphere[0])
    mesh.triangles = o3d.utility.Vector3iVector(source_icosphere[1])

    simplified: o3d.cuda.pybind.geometry.TriangleMesh = mesh.simplify_quadric_decimation(
        target_number_of_triangles=face_count
    )
    simplified.remove_duplicated_vertices()
    simplified.remove_unreferenced_vertices()

    if len(simplified.triangles) != face_count:
        print(f"Warning: Failed to simplify mesh exactly. Requested {face_count}, "
              f"got {len(simplified.triangles)} faces.")

    return np.asarray(simplified.vertices), np.asarray(simplified.triangles)


def signed_distance(collider0, collider1, transform1):
    """
    Returns the signed distance between the two colliders, after applying transform1 to collider1.
    """
    collider1.update_pose(transform1)
    dist, _, _, simplex, _ = gjk_distance_original(collider0, collider1)

    if dist > 0:
        return dist

    # Shapes are touching or overlapping: try to recover the penetration
    # depth via EPA, using the terminating simplex from GJK. If EPA fails, treat the distance as 0.
    try:
        mtv, _, success = epa(simplex, collider0, collider1)
        if success:
            depth = np.linalg.norm(mtv)
            if depth > 0:
                return -depth
    except Exception:
        pass

    return 0.0


def find_translation_for_target_distance(collider0, collider1, rotation1, axis, target_distance):
    """
    Use binary search to find the translation amount t along `axis` (collider1 is rotated by
    `rotation1`, collider0 is fixed at the origin) so that signed_distance(t) is
    as close as possible to `target_distance`.

    At t=0 both shapes are centered on the same point (maximal overlap).
    :return: (t, achieved_distance)
    """

    def eval_t(t):
        transform1 = np.eye(4)
        transform1[:3, :3] = rotation1
        transform1[:3, 3] = axis * t
        return signed_distance(collider0, collider1, transform1)

    lo, hi = 0, (3.0 * ICOSPHERE_RADIUS)
    f_hi = eval_t(hi)
    expand_attempts = 0
    while f_hi < target_distance and expand_attempts < 10:
        hi *= 1.5
        f_hi = eval_t(hi)
        expand_attempts += 1

    t_mid, f_mid = hi, f_hi
    for _ in range(100):
        t_mid = 0.5 * (lo + hi)
        f_mid = eval_t(t_mid)
        if abs(f_mid - target_distance) < 1e-6:
            break
        if f_mid < target_distance:
            lo = t_mid
        else:
            hi = t_mid

    if abs(f_mid - target_distance) > 1e-6:
        print(f"Warning: Failed to converge on solution for distance {target_distance}m, could only reach {f_mid}m")
    return t_mid, f_mid


vertices, triangles = build_fixed_icosphere(FACE_COUNT, ICOSPHERE_RADIUS)

collider0 = MeshGraph(np.eye(4), vertices, triangles)
collider1 = MeshGraph(np.eye(4), vertices, triangles)

collider_name = f"icosphere_{FACE_COUNT}faces_r{ICOSPHERE_RADIUS}"

metadata_rows = []
i = 0
for target_distance in TARGET_DISTANCES:
    for _ in range(NUM_POSES_PER_DISTANCE):
        rotation1 = Rotation.random(rng=rng).as_matrix()
        axis = rand_unit_vector()

        t, achieved_distance = find_translation_for_target_distance(
            collider0, collider1, rotation1, axis, target_distance
        )

        transform1 = np.eye(4)
        transform1[:3, :3] = rotation1
        transform1[:3, 3] = axis * t
        collider1.update_pose(transform1)

        cases = [((collider_name, collider0), (collider_name, collider1))]

        file_name = f"icospheres_fixed_size_distance_sweep_{i}.json"
        print(i, f"target={target_distance:.4g}  achieved={achieved_distance:.4g}")
        write_test_file(cases, subdirectory_name, file_name, clean_collider_names=False)

        metadata_rows.append((i, file_name, target_distance, achieved_distance))
        i += 1

metadata_path = os.path.join(subdirectory_name, "target_distances.csv")
with open(metadata_path, "w") as f:
    f.write("case,file_name,target_distance,achieved_distance\n")
    for row in metadata_rows:
        f.write("{},{},{:.8f},{:.8f}\n".format(*row))

print(f"\nGenerated {i} benchmark cases in '{subdirectory_name}'.")
print(f"Distance metadata written to '{metadata_path}'.")
