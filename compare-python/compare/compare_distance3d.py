import json

import numpy as np
import timeit

from distance3d.gjk import gjk_distance_original, gjk_intersection_jolt, gjk_distance_jolt, gjk_nesterov_accelerated, \
    gjk_nesterov_accelerated_primitives

from distance3d.colliders import MeshGraph

from src import load_test_file

cases = load_test_file("../data/current.json")


iterations = len(cases)

# The hill climbing of MeshGraph starts at the support vertex of its previous search. Reset it before every query,
# so that repeated runs do not reuse the result of the previous run (as for the C++ implementations).
support_caches = [[(collider._support_function, collider._support_function.first_idx)
                   for collider, _ in case if isinstance(collider, MeshGraph)] for case in cases]


def reset_support_caches(i):
    for support_function, first_idx in support_caches[i]:
        support_function.first_idx = first_idx


def benchmark_original():
    for i in range(iterations):
        reset_support_caches(i)
        gjk_distance_original(cases[i][0][0], cases[i][1][0])


def benchmark_jolt_intersection():
    for i in range(iterations):
        reset_support_caches(i)
        gjk_intersection_jolt(cases[i][0][0], cases[i][1][0])


def benchmark_jolt_distance():
    for i in range(iterations):
        reset_support_caches(i)
        gjk_distance_jolt(cases[i][0][0], cases[i][1][0])


def benchmark_nesterov_accelerated():
    for i in range(iterations):
        reset_support_caches(i)
        gjk_nesterov_accelerated(cases[i][0][0], cases[i][1][0], use_nesterov_acceleration=False)


def benchmark_nesterov_accelerated_with_acceleration():
    for i in range(iterations):
        reset_support_caches(i)
        gjk_nesterov_accelerated(cases[i][0][0], cases[i][1][0], use_nesterov_acceleration=True)


def benchmark_nesterov_accelerated_primitives():
    for i in range(iterations):
        reset_support_caches(i)
        gjk_nesterov_accelerated_primitives(cases[i][0][0], cases[i][1][0], use_nesterov_acceleration=False)


def benchmark_nesterov_accelerated_primitives_with_acceleration():
    for i in range(iterations):
        reset_support_caches(i)
        gjk_nesterov_accelerated_primitives(cases[i][0][0], cases[i][1][0], use_nesterov_acceleration=True)


# Warm-up: run all functions 10 times before the measurement, as for the other implementations.
# The first run forces numba to compile them, which avoids a constant overhead for the first time the benchmarks
# are run (simply using @njit(cache=True) does not seem to help with this).
for _ in range(10):
    benchmark_original()
    benchmark_jolt_intersection()
    benchmark_jolt_distance()
    benchmark_nesterov_accelerated()
    benchmark_nesterov_accelerated_with_acceleration()

result = {}

times = timeit.repeat(benchmark_original, repeat=10, number=1)
micro = np.median(times) * 1000000
result["Original"] = micro
print(f"Original: {micro:.2f}")



times = timeit.repeat(benchmark_jolt_intersection, repeat=10, number=1)
micro = np.median(times) * 1000000
result["Jolt (intersection)"] = micro
print(f"Jolt (intersection): {micro:.2f}")

times = timeit.repeat(benchmark_jolt_distance, repeat=10, number=1)
micro = np.median(times) * 1000000
result["Jolt (distance)"] = micro
print(f"Jolt (distance): {micro:.2f}")


times = timeit.repeat(benchmark_nesterov_accelerated, repeat=10, number=1)
micro = np.median(times) * 1000000
result["Nesterov"] = micro
print(f"Nesterov: {micro:.2f}")

times = timeit.repeat(benchmark_nesterov_accelerated_with_acceleration, repeat=10, number=1)
micro = np.median(times) * 1000000
result["Nesterov (with acceleration)"] = micro
print(f"Nesterov (with acceleration): {micro:.2f}")


file = open(f"./distance3d_result.json", "w")
json.dump(result, file, indent=4)