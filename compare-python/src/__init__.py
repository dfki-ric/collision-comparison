import random

import numpy as np

from .analyze import analyze_robot, get_collider_count, get_distances_all, get_distances_cases, get_colliders_from_pairs, \
    get_collider_sizes, get_average_size, plot_distance_distribution, print_collider_distribution
from .load_atlas import get_atlas_bvh
from .load_nao import get_nao_bvh, get_nao_bvh_complex
from .load_uc6 import get_uc6_bvh
from .load_ur10 import get_ur10_tm, get_u10_bvh_complex, get_ur10_bvh_from_tm
from .test_file import write_test_file, load_test_file

uc6_ur10_offset = np.eye(4)
uc6_ur10_offset[:3, 3] = np.array([1, -1, -1.5])

def set_random_joints(tm):
    for joint in tm._joints:
        limits = tm.get_joint_limits(joint)
        joint_pos = round(random.uniform(limits[0], limits[1]), 2)
        tm.set_joint(joint, joint_pos)



