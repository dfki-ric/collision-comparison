#!/bin/bash

cd compare/build_debug/
cmake -DBUILD_PYTHON_INTERFACE:BOOL=OFF ..
make -j8
cd ../..

