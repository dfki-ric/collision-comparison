from src import write_test_file, get_atlas_tm, set_random_joints, get_atlas_bvh_from_tm

tm = get_atlas_tm()

datasets = 100000
i = 0
while i <= datasets:
    set_random_joints(tm)

    bvh = get_atlas_bvh_from_tm(tm)

    cases = bvh.aabb_overlapping_with_self()
    if len(cases) > 0:
        print(i)
        write_test_file(cases, "../data", f"atlas_self_collision_{i}.json")
        i += 1
