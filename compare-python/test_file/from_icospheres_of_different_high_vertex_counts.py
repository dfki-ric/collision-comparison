import os
import random

import numpy as np
from scipy.spatial.transform import Rotation
import open3d as o3d

from distance3d.colliders import MeshGraph
from distance3d.hydroelastic_contact._tetra_mesh_creation import make_triangular_icosphere
from src import write_test_file


def rand_unit_vector():
    """
    Generate a 3D unit vector pointing in a random direction
    :return: The vector as numpy array
    """
    theta = rng.uniform(0, 2*np.pi)
    y = rng.uniform(-1,1)
    k = np.sqrt(1-y*y)
    return np.array([k*np.cos(theta), k*np.sin(theta), y])


subdirectory_name = "../data/icospheres_of_different_high_vertex_counts"
os.makedirs(subdirectory_name + "/meshes", exist_ok=True)

num_random_poses_per_vertex_count = 40
icosphere_radius = 0.5
i = 0

# to get reproducible benchmark cases, set the rng seed:
random.seed(42)
rng = np.random.default_rng(42)


# this range contains 20 face counts linearly from 50_000 to 1_000_000:
face_counts = np.arange(50_000, 1_050_000, step=50_000).astype(int)

# create an icosphere with enough faces so we can simplify it to create the icospheres with the desired face counts:

subdivs_needed_for_max_face_count = np.ceil(np.emath.logn(4, (face_counts[-1]/20.0))).astype(int)
source_icosphere = make_triangular_icosphere(center=np.array([0,0,0]), radius=icosphere_radius, order=subdivs_needed_for_max_face_count)


for face_count in face_counts:
    # simplify mesh to current face_count:
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(source_icosphere[0])
    mesh.triangles = o3d.utility.Vector3iVector(source_icosphere[1])

    simplified: o3d.cuda.pybind.geometry.TriangleMesh = mesh.simplify_quadric_decimation(
        target_number_of_triangles=face_count
    )
    simplified.remove_duplicated_vertices()
    simplified.remove_unreferenced_vertices()

    if len(simplified.triangles) > face_count:
        print(
            f"Warning: Failed to simplify mesh. Should have {face_count}, but still has {len(simplified.triangles)} faces")

    collider0 = MeshGraph(np.eye(4), np.asarray(simplified.vertices), np.asarray(simplified.triangles))
    collider1 = MeshGraph(np.eye(4), np.asarray(simplified.vertices), np.asarray(simplified.triangles))


    for _ in range(num_random_poses_per_vertex_count):
        # the first collider is placed at a random offset with random rotation:
        transform0 = np.eye(4)
        transform0[:3, :3] = Rotation.random(rng=rng).as_matrix()
        transform0[:3, 3] = rand_unit_vector() * rng.uniform(0.0,5.0)

        # the second collider is also rotated randomly:
        transform1 = np.eye(4)
        transform1[:3, :3] = Rotation.random(rng=rng).as_matrix()

        # the second collider gets translated some random amount between 0 and 2 * icosphere diameter,
        # starting from the position of collider0.
        # This way, the number of benchmark cases
        # where the spheres intersect will be about equal to the number where they don't.
        transform1[:3, 3] = transform0[:3, 3] + rand_unit_vector() * rng.uniform(0.0,4.0 * icosphere_radius)
        transform2 = np.eye(4)

        collider0.update_pose(transform0)
        collider1.update_pose(transform1)

        cases = [((f"icosphere_{face_count}faces", collider0), (f"icosphere_{face_count}faces", collider1))]

        print(i)
        write_test_file(
            cases,
            subdirectory_name,
            f"icospheres_of_different_high_vertex_counts_{i}.json",
            clean_collider_names=False,
            compute_convex_hulls=False,
        )
        i += 1
