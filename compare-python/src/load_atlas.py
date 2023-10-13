import numpy as np
from pytransform3d.urdf import UrdfTransformManager
from distance3d.broad_phase import BoundingVolumeHierarchy


def get_atlas_tm():
    data_path = "../data/urdfs/"
    urdf_file = "atlas.urdf"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path)

    return tm


def get_atlas_bvh_from_tm(tm, use_visuals=False, base_frame2origin=np.eye(4)):
    bvh = BoundingVolumeHierarchy(tm, "drc_skeleton", base_frame2origin=base_frame2origin)
    bvh.fill_tree_with_colliders(tm, make_artists=True, use_visuals=use_visuals)

    return bvh


def get_atlas_bvh():
    tm = get_atlas_tm()
    bvh = get_atlas_bvh_from_tm(tm)
    return tm, bvh
