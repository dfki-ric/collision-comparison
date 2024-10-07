import random

import numpy as np
from scipy.spatial.transform import Rotation

from .analyze import analyze_robot, get_collider_count, get_distances_all, get_distances_cases, get_colliders_from_pairs, \
    get_collider_sizes, get_average_size, plot_distance_distribution, print_collider_distribution
from .analyze_results import get_rust_results, get_cpp_result, get_python_results
from .load_atlas import get_atlas_tm, get_atlas_bvh_from_tm, get_atlas_bvh
from .load_nao import get_nao_bvh, get_nao_bvh_complex
from .load_uc1 import get_uc1_bvh
from .load_uc2 import get_uc2_bvh
from .load_uc5 import get_uc5_bvh
from .load_uc6 import get_uc6_bvh
from .load_ur10 import get_ur10_tm, get_u10_bvh_complex, get_ur10_bvh_from_tm
from .test_file import write_test_file, load_test_file

uc1_ur10_offset = np.eye(4)
uc1_ur10_offset[:3, :3] = Rotation.from_euler('xyz', [0, 0, -25], degrees=True).as_matrix()
uc1_ur10_offset[:3, 3] = np.array([0.3, 0.8, -1.23])

uc2_ur10_offset = np.eye(4)
uc2_ur10_offset[:3, :3] = Rotation.from_euler('xyz', [0, 0, 180], degrees=True).as_matrix()
uc2_ur10_offset[:3, 3] = np.array([0, 0, 0])

uc5_ur10_offset = np.eye(4)
uc5_ur10_offset[:3, 3] = np.array([0.37, 0.67, -1])

uc6_ur10_offset = np.eye(4)
uc6_ur10_offset[:3, 3] = np.array([1, -1, -1.5])

def set_random_joints(tm):
    for joint in tm._joints:
        limits = tm.get_joint_limits(joint)
        joint_pos = round(random.uniform(limits[0], limits[1]), 2)
        tm.set_joint(joint, joint_pos)
