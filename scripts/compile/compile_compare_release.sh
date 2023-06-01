#!/bin/bash

cd compare/build_debug/
cmake -DBUILD_PYTHON_INTERFACE:BOOL=OFF -DCMAKE_BUILD_TYPE=Release ..
make -j8
cd ../..

