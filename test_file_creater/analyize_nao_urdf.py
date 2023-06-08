from test_file_creater.analyze import get_collider_count, get_average_dist, get_colliders_from_pairs
from test_file_creater.load_nao import get_nao_bvh

data_path = "../data/"
bvh = get_nao_bvh(data_path)

colliders = bvh.get_colliders()

collider_count = get_collider_count(colliders)
average_dist = get_average_dist(colliders)

after_broard_phase_with_self = bvh.aabb_overlapping_with_self()
collider_after_broard = get_colliders_from_pairs(after_broard_phase_with_self)

collider_count_after_broard = get_collider_count(colliders)
average_dist_after_broard = get_average_dist(colliders)

print("Done")

