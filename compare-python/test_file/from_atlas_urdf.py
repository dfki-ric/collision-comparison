from src import get_atlas_bvh, write_test_file

tm, bvh = get_atlas_bvh()
cases = bvh.aabb_overlapping_with_self()
write_test_file(cases, "../data", "atlas_test_cases.json")

