#!/bin/bash
cd compare-rs
rm -rf target/criterion

source "$HOME/.cargo/env"
# --no-fail-fast: if one benchmark binary fails (e.g., collision-rs panics), still run the others
# BENCHMARK_FILTER (see benchmark_dataset.sh) selects benchmarks by name
if [ -n "$BENCHMARK_FILTER" ]; then
  cargo bench --no-fail-fast -- "$BENCHMARK_FILTER"
else
  cargo bench --no-fail-fast
fi
cd ..