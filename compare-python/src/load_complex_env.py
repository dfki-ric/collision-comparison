from pytransform3d.urdf import UrdfTransformManager

from distance3d.broad_phase import BoundingVolumeHierarchy


def get_complex_env_bvh(use_visuals=False):
    data_path = "../data/urdfs/complex_env/"
    urdf_file = "complex_env.urdf"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path, mesh_path=data_path)

    bvh = BoundingVolumeHierarchy(tm, "world")
    bvh.fill_tree_with_colliders(tm, make_artists=True, use_visuals=use_visuals)

    return tm, bvh


