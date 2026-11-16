#!/bin/bash
# see benchmark_dataset.sh; finer sweep of small icospheres for the thresholds of the adaptive support functions of
# libccd and OpenGJK (support function study of the paper, C++ only)
BENCHMARK_LANGUAGES=cpp BENCHMARK_FILTER="^(libccd|openGJK) " \
    bash scripts/benchmarks/benchmark_dataset.sh icospheres_threshold_sweep 0 2399
