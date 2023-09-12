#!/bin/bash
cd compare-python
../venv/bin/python3 compare/compare_distance3d.py
../venv/bin/python3 compare/compare_pybullet.py
cd ..