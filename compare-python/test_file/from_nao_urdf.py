from src import get_nao_bvh, write_test_file

tm, bvh = get_nao_bvh()
cases = bvh.aabb_overlapping_with_self()
write_test_file(cases, "../data", "nao_test_cases.json")





