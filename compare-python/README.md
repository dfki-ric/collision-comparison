# Compare Python

This Project contains all the python code. For test case creation, python benchmarking and result analysis.

## Structure 
- analyze -> compile the results into CSV files and analyze them (run_analysis.py, see README.md in the repository root)
- compare -> benchmarking code executed when running benchmark
- debug -> show the models, strip the results-archive
- test_file -> create test data
- src -> helper functions

```bash
cd ..
sh ./scripts/benchmarks/benchmark_python.sh
```
Performs the benchmark on the data/current.json file for distance3d and pybullet.

