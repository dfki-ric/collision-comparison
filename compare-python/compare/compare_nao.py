import json

import numpy as np
import timeit

from distance3d.gjk import gjk_distance_original, gjk_intersection_jolt, gjk_distance_jolt, gjk_nesterov_accelerated, \
    gjk_nesterov_accelerated_primitives

from src import get_nao_bvh

tm, bvh = get_nao_bvh()
shapes = bvh.aabb_overlapping_with_self()
iterations = len(shapes)


def benchmark_original():
    for i in range(iterations):
        gjk_distance_original(shapes[i][0][1], shapes[i][1][1])


def benchmark_jolt_intersection():
    for i in range(iterations):
        gjk_intersection_jolt(shapes[i][0][1], shapes[i][1][1])


def benchmark_jolt_distance():
    for i in range(iterations):
        gjk_distance_jolt(shapes[i][0][1], shapes[i][1][1])


def benchmark_nesterov_accelerated():
    for i in range(iterations):
        gjk_nesterov_accelerated(shapes[i][0][1], shapes[i][1][1], use_nesterov_acceleration=False)


def benchmark_nesterov_accelerated_with_acceleration():
    for i in range(iterations):
        gjk_nesterov_accelerated(shapes[i][0][1], shapes[i][1][1], use_nesterov_acceleration=True)


def benchmark_nesterov_accelerated_primitives():
    for i in range(iterations):
        gjk_nesterov_accelerated_primitives(shapes[i][0][1], shapes[i][1][1], use_nesterov_acceleration=False)


def benchmark_nesterov_accelerated_primitives_with_acceleration():
    for i in range(iterations):
        gjk_nesterov_accelerated_primitives(shapes[i][0][1], shapes[i][1][1], use_nesterov_acceleration=True)


result = {}

times = timeit.repeat(benchmark_original, repeat=10, number=1)
micro = np.mean(times) * 1000000
result["Original"] = micro
print(f"Original: {micro:.2f}")



times = timeit.repeat(benchmark_jolt_intersection, repeat=10, number=1)
micro = np.mean(times) * 1000000
result["Jolt (intersection)"] = micro
print(f"Jolt (intersection): {micro:.2f}")

times = timeit.repeat(benchmark_jolt_distance, repeat=10, number=1)
micro = np.mean(times) * 1000000
result["Jolt (distance)"] = micro
print(f"Jolt (distance): {micro:.2f}")


times = timeit.repeat(benchmark_nesterov_accelerated, repeat=10, number=1)
micro = np.mean(times) * 1000000
result["Nesterov"] = micro
print(f"Nesterov: {micro:.2f}")

times = timeit.repeat(benchmark_nesterov_accelerated_with_acceleration, repeat=10, number=1)
micro = np.mean(times) * 1000000
result["Nesterov (with acceleration)"] = micro
print(f"Nesterov (with acceleration): {micro:.2f}")


times = timeit.repeat(benchmark_nesterov_accelerated_primitives, repeat=10, number=1)
micro = np.mean(times) * 1000000
result["Nesterov (Primitives)"] = micro
print(f"Nesterov (Primitives): {micro:.2f}")

times = timeit.repeat(benchmark_nesterov_accelerated_primitives_with_acceleration, repeat=10, number=1)
micro = np.mean(times) * 1000000
result["Nesterov (Primitives with acceleration)"] = micro
print(f"Nesterov (Primitives with acceleration): {micro:.2f}")

file = open(f"./distance3d_result.json", "w")
json.dump(result, file, indent=4)