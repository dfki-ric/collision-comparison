#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:collision-comparison/compare-python" 

source ~/.bashrc

source /opt/miniconda/bin/activate collision_env


cd compare-python
python3 compare/compare_distance3d.py
python3 compare/compare_pybullet.py
cd ..