import os
import random

from src import write_test_file, set_random_joints, get_tiago_tm, get_tiago_bvh_from_tm, get_tiago_disabled_link_pairs, collider_link

# Self-collision of TIAGo with the Hey5 hand, which has mesh and primitive colliders (box, cylinder, sphere).
# A case file contains all collider pairs of one random joint configuration whose AABBs overlap, except for the
# link pairs that are excluded from self-collision checks (see get_tiago_disabled_link_pairs).
tm = get_tiago_tm()
bvh = get_tiago_bvh_from_tm(tm)
disabled = get_tiago_disabled_link_pairs()

subdirectory_name = "../data/tiago_self_collision"
os.makedirs(subdirectory_name + "/meshes", exist_ok=True)
datasets = 1000
i = 0

# to get reproducible benchmark cases, set the rng seed:
random.seed(42)
while i <= datasets:
    set_random_joints(tm)
    bvh.update_collider_poses()

    # every pair is reported in both orders
    cases = {}
    for collider0, collider1 in bvh.aabb_overlapping_with_self():
        links = frozenset((collider_link(collider0[0]), collider_link(collider1[0])))
        key = tuple(sorted((collider0[0], collider1[0])))
        if links not in disabled and key not in cases:
            cases[key] = (collider0, collider1)
    if len(cases) > 0:
        print(i)
        write_test_file([cases[key] for key in sorted(cases)], subdirectory_name, f"tiago_self_collision_{i}.json")
        i += 1
