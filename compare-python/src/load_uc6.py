from pytransform3d.urdf import UrdfTransformManager

from distance3d.broad_phase import BoundingVolumeHierarchy


def get_uc6_bvh(use_visuals=False):
    data_path = "../data/urdfs/"
    urdf_file = "uc6_ines.urdf"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path)

    bvh = BoundingVolumeHierarchy(tm, "uc6_ines")
    bvh.fill_tree_with_colliders(tm, make_artists=True, use_visuals=use_visuals)

    return tm, bvh


