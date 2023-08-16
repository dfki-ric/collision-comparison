#!/bin/bash

cd compare-cpp/build_release/
cmake -DBUILD_PYTHON_INTERFACE:BOOL=OFF -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --target compare -j 8
cd ../..

