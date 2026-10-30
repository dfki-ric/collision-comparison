import os
import random

from src import write_test_file, set_random_joints, get_complex_env_bvh, get_dual_arm_tm, complex_env_dual_arm_offset, get_dual_arm_bvh_from_tm

use_visual_meshes = True

complex_env_tm, complex_env_bvh = get_complex_env_bvh(use_visuals=use_visual_meshes)
dual_arm_tm = get_dual_arm_tm()

subdirectory_name = "../data/complex_env_dual_arm_collision"
os.makedirs(subdirectory_name + "/meshes", exist_ok=True)
datasets = 1000
i = 0

# to get reproducible benchmark cases, set the rng seed:
random.seed(42)
while i <= datasets:
    set_random_joints(dual_arm_tm)

    dual_arm_bvh = get_dual_arm_bvh_from_tm(dual_arm_tm, base_frame2origin=complex_env_dual_arm_offset, use_visuals=use_visual_meshes)

    cases = complex_env_bvh.aabb_overlapping_with_other_bvh(dual_arm_bvh)
    if len(cases) > 0:
        print(i)
        write_test_file(cases, subdirectory_name, f"complex_env_dual_arm_collision_{i}.json")
        i += 1
