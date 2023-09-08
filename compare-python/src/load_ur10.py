import random

import numpy as np
from pytransform3d.urdf import UrdfTransformManager

from distance3d.broad_phase import BoundingVolumeHierarchy

def get_ur10_tm():
    data_path = "../data/urdfs/"
    urdf_file = "mia_hand_on_ur10.urdf"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path)

    return tm

def get_ur10_bvh_from_tm(tm, use_visuals=False, base_frame2origin=np.eye(4)):
    bvh = BoundingVolumeHierarchy(tm, "mia_hand_on_ur10", base_frame2origin=base_frame2origin)
    bvh.fill_tree_with_colliders(tm, make_artists=True, use_visuals=use_visuals)

    return bvh


def get_u10_bvh_complex(use_visuals=False):
    data_path = "../data/urdfs/ur/"
    urdf_file = "april_robot_description/urdf/mia_hand_on_ur10.urdf"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path + "universal_robot/")

    bvh = BoundingVolumeHierarchy(tm, "mia_hand_on_ur10")
    bvh.fill_tree_with_colliders(tm, make_artists=True, use_visuals=use_visuals)

    return tm, bvh


