#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:collision-comparison/compare-python" 

cd compare-python
../venv/bin/python3 compare/compare_distance3d.py
../venv/bin/python3 compare/compare_pybullet.py
cd ..