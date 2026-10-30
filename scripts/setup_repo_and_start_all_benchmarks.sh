#!/bin/bash
source ~/.bashrc

source /opt/miniconda/bin/activate collision_env

bash scripts/repo_setup.sh

# Run all benchmarks of the paper (UR10 use cases 1, 2, 5, 6 and the dual-arm scene); the commented benchmarks are
# not part of the paper:
# Every benchmark stores its results in results/<dataset>/ before compiling them into a CSV. Case files that already
# have results are skipped, so this script can be restarted after an interruption and continues where it stopped.

bash scripts/benchmarks/benchmark_uc1_ur10.sh

bash scripts/benchmarks/benchmark_uc2_ur10.sh

bash scripts/benchmarks/benchmark_uc5_ur10.sh

bash scripts/benchmarks/benchmark_uc6_ur10.sh

bash scripts/benchmarks/benchmark_complex_scene.sh

# bash scripts/benchmarks/benchmark_complex_scene_max256verts.sh

# bash scripts/benchmarks/benchmark_icospheres.sh

# bash scripts/benchmarks/benchmark_high_vertex_count_icospheres.sh

# bash scripts/benchmarks/benchmark_icospheres_fixed_size_distance_sweep.sh
