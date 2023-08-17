#!/bin/bash

echo --- CPP ---
sh scripts/benchmarks/benchmark_cpp.sh

echo --- RUST ---
sh scripts/benchmarks/benchmark_rust.sh

echo --- Python ---
sh scripts/benchmarks/benchmark_python.sh