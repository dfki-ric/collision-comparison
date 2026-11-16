#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/compare-python"


source /opt/miniconda/bin/activate collision_env


cd compare-python
# pinned to one core (BENCHMARK_CORE, default 2), as the C++ and Rust benchmarks
taskset -c "${BENCHMARK_CORE:-2}" python3 compare/compare_distance3d.py
taskset -c "${BENCHMARK_CORE:-2}" python3 compare/compare_pybullet.py
cd ..