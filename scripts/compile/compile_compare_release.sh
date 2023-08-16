#!/bin/bash

cd compare-cpp/build_release/
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_MAKE_PROGRAM=ninja -DBUILD_PYTHON_INTERFACE:BOOL=OFF -G Ninja -S .. -B .
cmake --build . --target compare -j 6
cd ../..

