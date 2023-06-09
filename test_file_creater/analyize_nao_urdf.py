from test_file_creater.analyze import get_collider_count, get_distances_all, get_colliders_from_pairs, \
    plot_distance_distribution, print_collider_distribution, get_collider_sizes, get_average_size, get_distances_cases
from test_file_creater.load_nao import get_nao_bvh

data_path = "../data/"
bvh = get_nao_bvh(data_path)

colliders = bvh.get_colliders()

collider_count = get_collider_count(colliders)
distances, average_dist = get_distances_all(colliders)
sizes = get_collider_sizes(colliders)
average_size = get_average_size(sizes)

after_broad_phase_with_self = bvh.aabb_overlapping_with_self()
collider_after_broad = get_colliders_from_pairs(after_broad_phase_with_self)
collider_count_after_broad = get_collider_count(collider_after_broad)

distances_after_broad, average_dist_after_broad = get_distances_cases(after_broad_phase_with_self)
sizes_after_broad = get_collider_sizes(collider_after_broad)
average_size_after_broad = get_average_size(sizes_after_broad)

print("---- Without Broad Phase ----")
print("Colliders: ", len(colliders))

print_collider_distribution(collider_count)

print("Average Size: ", average_size)

print("Collision Cases: ", (len(colliders) * len(colliders)) - len(colliders))
print("Average Distance: ", average_dist)
plot_distance_distribution(distances, "Distance Distribution")

print("---- With Broad Phase ----")
print("Colliders: ", len(collider_after_broad))

print_collider_distribution(collider_count)

print("Average Size: ", average_size_after_broad)

print("Collision Cases: ", len(after_broad_phase_with_self))
print("Average Distance: ", average_dist_after_broad)
plot_distance_distribution(distances_after_broad, "Distance Distribution after broad phase")

print("Done")


