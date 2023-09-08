from src import get_ur10_tm, get_ur10_bvh_from_tm, write_test_file

tm = get_ur10_tm()
bvh = get_ur10_bvh_from_tm(tm)
cases = bvh.aabb_overlapping_with_self()
write_test_file(cases, "../data", "ur10_test_cases.json")
