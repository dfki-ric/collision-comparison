import numpy as np
from pytransform3d.urdf import UrdfTransformManager
from scipy.spatial.transform import Rotation

from distance3d.broad_phase import BoundingVolumeHierarchy
from src import write_test_file
import os

def get_tm_from_urdf(data_path:str, urdf_file:str) -> UrdfTransformManager:
    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path, mesh_path=data_path)
    return tm

def get_bvh_from_tm(tm: UrdfTransformManager, use_visuals=False, base_frame2origin=np.eye(4)) -> BoundingVolumeHierarchy:
    bvh = BoundingVolumeHierarchy(tm, "world", base_frame2origin=base_frame2origin)
    bvh.fill_tree_with_colliders(tm, make_artists=True, use_visuals=use_visuals)
    return bvh

def get_bvh_from_urdf(data_path:str, urdf_file:str, use_visuals=False, base_frame2origin=np.eye(4)) -> BoundingVolumeHierarchy:
    tm = get_tm_from_urdf(data_path, urdf_file)
    bvh = get_bvh_from_tm(tm, use_visuals, base_frame2origin)
    return bvh


use_visual_meshes = True

tetrahedron1_bvh = get_bvh_from_urdf(
    data_path="../data/urdfs/tetrahedron/",
    urdf_file="tetrahedron_scene.urdf",
    use_visuals=use_visual_meshes
)
transform = np.eye(4)
transform[:3, :3] = Rotation.from_euler('xyz', [0, 0, 0], degrees=True).as_matrix()
transform[:3, 3] = np.array([2, 0, 0])

tetrahedron2_bvh = get_bvh_from_urdf(
    data_path="../data/urdfs/tetrahedron/",
    urdf_file="tetrahedron_scene.urdf",
    use_visuals=use_visual_meshes,
    base_frame2origin=transform
)


cases = [(
list(tetrahedron1_bvh.colliders_.items())[0],
list(tetrahedron2_bvh.colliders_.items())[0]
)]

subdirectory_name = "../data/tetrahedron_collision"
os.makedirs(subdirectory_name + "/meshes", exist_ok=True)


write_test_file(cases, subdirectory_name, f"tetrahedron_collision.json")
