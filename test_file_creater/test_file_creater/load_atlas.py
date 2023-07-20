from distance3d.broad_phase import BoundingVolumeHierarchy
from pytransform3d.urdf import UrdfTransformManager


def get_atlas_bvh(data_path, use_visuals=False):
    urdf_file = "modified/atlas_v5_simple_shapes.urdf"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path)

    bvh = BoundingVolumeHierarchy(tm, "drc_skeleton")
    bvh.fill_tree_with_colliders(tm, make_artists=True, use_visuals=use_visuals)

    return tm, bvh
