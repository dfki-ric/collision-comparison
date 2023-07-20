from distance3d.broad_phase import BoundingVolumeHierarchy
from pytransform3d.urdf import UrdfTransformManager


def get_nao_bvh(data_path, use_visuals=False):
    urdf_file = "only_primitives/urdf/NaoH25V40.urdf"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path + "../")

    bvh = BoundingVolumeHierarchy(tm, "NaoH25V40")
    bvh.fill_tree_with_colliders(tm, make_artists=True, use_visuals=use_visuals)

    return tm, bvh


def get_nao_bvh_complex(data_path, use_visuals=False):
    urdf_file = "nao_robot/nao_description/urdf/naoV40_generated_urdf/nao.urdf"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path)

    bvh = BoundingVolumeHierarchy(tm, "NaoH25V40")
    bvh.fill_tree_with_colliders(tm, make_artists=True, use_visuals=use_visuals)

    return tm, bvh
