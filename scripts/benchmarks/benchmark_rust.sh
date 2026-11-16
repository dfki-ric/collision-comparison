#!/bin/bash
cd compare-rs
rm -rf target/criterion

source "$HOME/.cargo/env"
# --no-fail-fast: if one benchmark binary fails (e.g., collision-rs panics), still run the others
# BENCHMARK_FILTER (see benchmark_dataset.sh) selects benchmarks by name; pinned to one core (BENCHMARK_CORE, default 2)
if [ -n "$BENCHMARK_FILTER" ]; then
  taskset -c "${BENCHMARK_CORE:-2}" cargo bench --no-fail-fast -- "$BENCHMARK_FILTER"
else
  taskset -c "${BENCHMARK_CORE:-2}" cargo bench --no-fail-fast
fi
cd ..