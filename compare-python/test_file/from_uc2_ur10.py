import random

from src import get_ur10_tm, get_ur10_bvh_from_tm, write_test_file, get_uc2_bvh, uc2_ur10_offset, set_random_joints

uc2_tm, uc2_bvh = get_uc2_bvh()
ur10_tm = get_ur10_tm()

datasets = 10000
i = 1
while i <= datasets:
    set_random_joints(ur10_tm)

    ur10_bvh = get_ur10_bvh_from_tm(ur10_tm, base_frame2origin=uc2_ur10_offset)

    cases = uc2_bvh.aabb_overlapping_with_other_bvh(ur10_bvh)
    if len(cases) > 0:
        print(i)
        write_test_file(cases, "../data", f"uc2_ur10_collision_{i}.json")
        i += 1
