#!/bin/bash
source ~/.bashrc

source /opt/miniconda/bin/activate collision_env

bash scripts/repo_setup.sh

# clean up old results if an earlier benchmark was interrupted:
rm -rf "compare-python/pybullet_result.json"
rm -rf "compare-python/distance3d_result.json"
rm -rf "compare-cpp/cpp_result.json"
rm -rf "compare-rs/target/criterion"

# Run all benchmarks:
# Every benchmark stores its results in ./results before compiling the results into a CSV,
# so make sure to remove the results of old benchmarks before starting new ones:
rm -rf results/*

bash scripts/benchmarks/benchmark_uc1_ur10.sh

rm -rf results/*

bash scripts/benchmarks/benchmark_complex_scene.sh

rm -rf results/*

bash scripts/benchmarks/benchmark_complex_scene_max256verts.sh

rm -rf results/*

bash scripts/benchmarks/benchmark_icospheres.sh

rm -rf results/*

bash scripts/benchmarks/benchmark_high_vertex_count_icospheres.sh

rm -rf results/*

bash scripts/benchmarks/benchmark_icospheres_fixed_size_distance_sweep.sh
