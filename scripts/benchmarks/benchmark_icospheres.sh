#!/bin/bash

i=0
until [ $i -gt 1999 ]
do
  echo i: $i

   if [ ! -d "results/$i" ]; then

    rm -f "data/current.json"
    ln -s "icospheres_of_different_vertex_counts/icospheres_of_different_vertex_counts_$i.json" "data/current.json"

    echo --- CPP ---
    bash scripts/benchmarks/benchmark_cpp.sh

    echo --- RUST ---
    bash scripts/benchmarks/benchmark_rust.sh

    echo --- Python ---
    bash scripts/benchmarks/benchmark_python.sh

    echo --- Copy Result ---
    mkdir "results/$i"
    mv "compare-python/pybullet_result.json" "results/$i/";
    mv "compare-python/distance3d_result.json" "results/$i/";
    mv "compare-cpp/cpp_result.json" "results/$i/";
    mv "compare-rs/target/criterion" "results/$i/";
   fi
  ((i=i+1))

done

python3 compare-python/analyze_new/compile_CSV_from_results.py results data/icospheres_of_different_vertex_counts

