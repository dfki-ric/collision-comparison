#!/bin/bash
# Runs the benchmarks of all implementations on the case files <first> to <last> of the dataset in data/<dataset>/
# and compiles the results into a CSV file.
#
# The results of each case file are stored in results/<dataset>/<case file number>/. Case files that already have
# results are skipped, so the benchmark can be restarted after an interruption and continues where it stopped.
#
# Usage: bash scripts/benchmarks/benchmark_dataset.sh <dataset> <first case file> <last case file>

if [ $# -ne 3 ]; then
  echo "Usage: bash scripts/benchmarks/benchmark_dataset.sh <dataset> <first case file> <last case file>"
  exit 1
fi
dataset=$1
first=$2
last=$3
results_dir="results/$dataset"
mkdir -p "$results_dir"

for ((i = first; i <= last; i++)); do
  echo "$dataset: case file $i"
  if [ -d "$results_dir/$i" ]; then
    continue
  fi

  # remove outputs of an interrupted run, so that they cannot end up in the results of this case file
  rm -f compare-cpp/cpp_result.json compare-python/distance3d_result.json compare-python/pybullet_result.json
  rm -rf compare-rs/target/criterion

  rm -f data/current.json
  cp "data/$dataset/${dataset}_$i.json" data/current.json

  echo --- CPP ---
  bash scripts/benchmarks/benchmark_cpp.sh

  echo --- RUST ---
  bash scripts/benchmarks/benchmark_rust.sh

  echo --- Python ---
  bash scripts/benchmarks/benchmark_python.sh

  echo --- Copy Result ---
  # collect the results in a temporary folder and rename it at the end: an interruption must not leave an
  # incomplete results folder behind, which would be skipped after a restart
  partial="$results_dir/$i.partial"
  rm -rf "$partial"
  mkdir "$partial"
  mv compare-python/pybullet_result.json compare-python/distance3d_result.json compare-cpp/cpp_result.json "$partial/"
  mv compare-rs/target/criterion "$partial/"
  mv "$partial" "$results_dir/$i"
done

python3 compare-python/analyze/compile_csv_from_results.py "$results_dir" "data/$dataset"
