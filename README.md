
# Benchmarking Convex-Convex Collision Detection for Robotics

Thilo Umland $^1$,
Maarten Behn $^2$,
Alexander Fabisch $^2$

$^1$ University of Bremen,
Bibliothekstraße 1,
D-28359 Bremen,
Germany

$^2$ Robotics Innovation Center, DFKI GmbH,
Robert-Hooke-Straße 1,
D-28359 Bremen,
Germany

## Abstract
Collision detection and distance calculation is needed in simulation, planning, and control.
In particular, Gilbert-Johnson-Keerthi (GJK) and its variations are widely used.
We are interested in the question of how programming language, algorithm engineering, and implementation tricks influence its performance.
We develop a benchmark that resembles how GJK is used in a highly optimized collision detection pipeline for an arm with an anthropomorphic hand and compare the performance of commonly used implementations of GJK.
We analyze not just the moments of the distribution of runtimes, but the whole distribution, which is relevant for real-time applications.

<img src="./doc/usecases.svg" width="800" />

## Folder-Structure
- [compare-cpp/README](./compare-cpp/README.md)
- [compare-rs/README](./compare-rs/README.md)
- [compare-python/README](./compare-python/README.md)
- [scripts/README](./scripts/README.md)

## Setup with Docker

The Docker image contains the system packages, Rust, and the conda environment `collision_env` with the Python
dependencies. The libraries are downloaded and built inside the repository, which is mounted into the container,
so builds and results stay on the host.

### 1. Build the image
```bash
docker buildx build -t compare .
```

### 2. Start a container
From the root of the repository:
```bash
docker run --mount type=bind,source=".",target="/collision-comparison" --rm -it --entrypoint bash compare
cd /collision-comparison
```
The conda environment `collision_env` is activated automatically.
Alternatively, open the repository as a dev container (see `.devcontainer/devcontainer.json`).

### 3. Set up the repository
```bash
bash scripts/repo_setup.sh
```
This unpacks the benchmark data, downloads and builds the libraries, and compiles the C++ benchmark.
The script can be run again: existing data, repositories and builds are kept.

### 4. Generate additional benchmark case files
The case files of the benchmark "icospheres_of_different_high_vertex_counts" are too large for GitHub
(about 500 MiB), so they have to be generated:
```bash
cd compare-python
PYTHONPATH=. python test_file/from_icospheres_of_different_high_vertex_counts.py
cd ..
```

### 5. Run the benchmarks
Run all benchmarks (this takes about 48 hours). The script runs the setup, all benchmarks, and compiles the results
into CSV files:
```bash
bash scripts/setup_repo_and_start_all_benchmarks.sh
```

To run only specific benchmarks, comment out the others in `scripts/setup_repo_and_start_all_benchmarks.sh`,
or run the scripts in `scripts/benchmarks` directly, e.g., `bash scripts/benchmarks/benchmark_uc1_ur10.sh`.
The results of each case file are stored in `results/`, and case files that already have results are skipped,
so empty `results/` before you start a different benchmark.

## Results
### How many Folders are done?
```bash
cd results
tree -L 1 | tail -1
```

### Analyzing Results
The CSV files generated during the previous step can be used in the evaluation notebooks located in `compare-python/analyze_new`.
Every row in a CSV file contains the time per collision query (median of the repetitions) for every algorithm, for that case file.

## Funding

This project has been developed initially at the Robotics Innovation Center
of the German Research Center for Artificial Intelligence (DFKI GmbH) in
Bremen. At this phase the work was supported through a grant from the European
Commission (870142).

<img src="doc/DFKI_RIC_RGB.png" height="100px" />
