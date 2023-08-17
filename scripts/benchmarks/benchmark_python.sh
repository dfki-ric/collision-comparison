#!/bin/bash
cd compare-python
../venv/bin/python3 compare/compare_nao.py
../venv/bin/python3 compare/compare_nao_pybullet.py
cd ..