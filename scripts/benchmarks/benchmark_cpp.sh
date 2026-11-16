#!/bin/bash
cd compare-cpp
# pinned to one core (BENCHMARK_CORE, default 2): unpinned runs on a not fully idle machine were up to 1.6 times slower
taskset -c "${BENCHMARK_CORE:-2}" ./build_release/compare
cd ../..