#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:collision-comparison/compare-python"

cd compare-python
python3 analyze/analyze_results_archive.py