#!/bin/bash
# Runs the benchmarks of all implementations on the case files <first> to <last> of the dataset in data/<dataset>/
# and compiles the results into a CSV file.
#
# The results of each case file are stored in results/<dataset>/<case file number>/. Case files that already have
# results are skipped, so the benchmark can be restarted after an interruption and continues where it stopped.
#
# A case file is only finished if the results of all languages exist. Otherwise (missing case file, crashed
# benchmark), it is listed in results/<dataset>/failures.log and gets no results folder, so it is run again after a
# restart. The script exits with an error if any case file failed. (A single missing Rust benchmark, e.g., because
# collision-rs panics, does not count as a failure, see compare-rs/benches/collision-rs.rs.)
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

if [ ! -d "data/$dataset" ]; then
  echo "Error: data/$dataset does not exist (see README.md: unzipped by scripts/repo_setup.sh or generated)"
  exit 1
fi
mkdir -p "$results_dir"
n_failures=0

fail() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') Error: $dataset, case file $i: $1" | tee -a "$results_dir/failures.log"
  n_failures=$((n_failures + 1))
}

for ((i = first; i <= last; i++)); do
  echo "$dataset: case file $i"
  if [ -d "$results_dir/$i" ]; then
    continue
  fi

  # remove outputs of an interrupted run, so that they cannot end up in the results of this case file
  rm -f compare-cpp/cpp_result.json compare-python/distance3d_result.json compare-python/pybullet_result.json
  rm -rf compare-rs/target/criterion

  case_file="data/$dataset/${dataset}_$i.json"
  if [ ! -f "$case_file" ]; then
    fail "$case_file does not exist"
    continue
  fi
  rm -f data/current.json
  cp "$case_file" data/current.json

  echo --- CPP ---
  bash scripts/benchmarks/benchmark_cpp.sh

  echo --- RUST ---
  bash scripts/benchmarks/benchmark_rust.sh

  echo --- Python ---
  bash scripts/benchmarks/benchmark_python.sh

  # the benchmark scripts do not report errors, so check that every language produced results
  missing=""
  for output in compare-cpp/cpp_result.json compare-rs/target/criterion \
                compare-python/distance3d_result.json compare-python/pybullet_result.json; do
    [ -e "$output" ] || missing="$missing $output"
  done
  if [ -n "$missing" ]; then
    fail "no results:$missing"
    continue
  fi

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

if [ $n_failures -gt 0 ]; then
  echo "Error: $n_failures case files of $dataset failed, see $results_dir/failures.log. Restart to run them again."
  exit 1
fi
