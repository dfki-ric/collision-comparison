from distance3d.broad_phase import BoundingVolumeHierarchy
from pytransform3d.urdf import UrdfTransformManager


def get_atlas_bvh(data_path):
    urdf_file = "urdfs/vigir_atlas_common/atlas_description/urdf/atlas_v5_simple_shapes.urdf"
    urdf_working_dir = "urdfs/"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path + urdf_working_dir)

    bvh = BoundingVolumeHierarchy(tm, "drc_skeleton")
    bvh.fill_tree_with_colliders(tm, make_artists=False)

    return bvh
