import numpy as np

from src import get_u10_bvh, write_test_file, get_uc6_bvh

ur10_offset = np.eye(4)
ur10_offset[:3, 3] = np.array([1, -1, -1.5])

uc6_tm, uc6_bvh = get_uc6_bvh()
ur10_tm, ur10_bvh = get_u10_bvh(base_frame2origin=ur10_offset)

cases = uc6_bvh.aabb_overlapping_with_other_bvh(ur10_bvh)
write_test_file(cases, "../data", "ur10_test_cases.json")
