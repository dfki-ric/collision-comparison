#!/bin/bash

cd compare-cpp/build_debug/
cmake -DBUILD_PYTHON_INTERFACE:BOOL=OFF ..
make -j8
cd ../..
