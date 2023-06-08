from distance3d.broad_phase import BoundingVolumeHierarchy
from pytransform3d.urdf import UrdfTransformManager


def get_nao_bvh(data_path):
    urdf_file = "urdfs/nao_robot/nao_description/urdf/naoV40_generated_urdf/nao.urdf"
    urdf_working_dir = "urdfs/"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path + urdf_working_dir)

    bvh = BoundingVolumeHierarchy(tm, "NaoH25V40")
    bvh.fill_tree_with_colliders(tm, make_artists=False)

    return bvh
