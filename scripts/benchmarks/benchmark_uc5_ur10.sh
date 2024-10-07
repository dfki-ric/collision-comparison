#!/bin/bash

until [ $i -gt 9999 ]
do
  echo i: $i
  ((i=i+1))

   if [ ! -d "results/$i" ]; then

    rm -f "data/current.json"
    cp "data/uc5_ur10_collision/uc5_ur10_collision_$i.json" "data/current.json"

    echo --- CPP ---
    sh scripts/benchmarks/benchmark_cpp.sh

    echo --- RUST ---
    sh scripts/benchmarks/benchmark_rust.sh

    echo --- Python ---
    sh scripts/benchmarks/benchmark_python.sh

    echo --- Copy Result ---
    mkdir "results/$i"
    cp "compare-python/pybullet_result.json" "results/$i/";
    cp "compare-python/distance3d_result.json" "results/$i/";
    cp "compare-cpp/cpp_result.json" "results/$i/";
    cp -a "compare-rs/target/criterion" "results/$i/";
   fi
done


