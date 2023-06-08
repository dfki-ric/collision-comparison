from test_file_creater.analyze import get_collider_count, get_distances, get_colliders_from_pairs, \
    plot_distance_distribution, print_collider_distribution
from test_file_creater.load_nao import get_nao_bvh

data_path = "../data/"
bvh = get_nao_bvh(data_path)

colliders = bvh.get_colliders()

collider_count = get_collider_count(colliders)
distances, average_dist = get_distances(colliders)

after_broad_phase_with_self = bvh.aabb_overlapping_with_self()
collider_after_broad = get_colliders_from_pairs(after_broad_phase_with_self)

collider_count_after_broad = get_collider_count(colliders)
distances_after_broad, average_dist_after_broad = get_distances(colliders)


print("Average Distance: ", average_dist)
print_collider_distribution(collider_count)
plot_distance_distribution(distances, "Distance Distribution")

# print("---- After Broad Phase ----")
# print("Average Distance: ", average_dist_after_broad)

# plot_distance_distribution(distances_after_broad, "Distance Distribution after broad phase")

print("Done")

