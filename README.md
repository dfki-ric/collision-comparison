
# Benchmarking Convex-Convex Collision Detection for Robotics

Maarten Behn $^1$,
Alexander Fabisch $^1$

$^1$ Robotics Innovation Center, DFKI GmbH,
Robert-Hooke-Straße 1,
D-28359 Bremen,
Germany

## Abstract
Collision detection and distance calculation is needed in simulation, planning, and control.
In particular, Gilbert-Johnson-Keerthi (GJK) and its variations are widely used.
We are interested in the question of how programming language, algorithm engineering, and implementation tricks influence its performance.
We develop a benchmark that resembles how GJK is used in a highly optimized collision detection pipeline for an arm with an anthropomorphic hand and compare the performance of commonly used implementations of GJK.
We analyze not just the moments of the distribution of runtimes, but the whole distribution, which is relevant for real-time applications.
Surprisingly, we obtain one of the best performances with the Jolt game engine, which is usually not used in robotics and does not implement the latest algorithmic developments.
We also found that highly optimized C++ libraries are still considerably faster than more recently developed Rust libraries, and that Python cannot be used when performance is a constraint, even when highly optimized, compiled code is called.
Statistical tests show that differences between the most commonly used C++ libraries are significant, but the effect size is often negligible.

<img src="./doc/usecases.svg" width="800" />

## Results

### Runtime Distributions

![Violin Plot](./doc/violin.svg)

### Results on PC1

Results of hypothesis testing for time per collision test *on PC1*. The alternative hypothesis is $T_{\text{row}} < T_{\text{column}}$. *ns* indicates not significant results, i.e., $T_{\text{row}} \geq T_{\text{column}}$ was not rejected. When the result is significant, we report the common language effect size (percentage of runtimes of the algorithm given in the row that are greater than runtimes of the algorithm in the column in pairwise comparisons, 0 indicates the largest effect).

#### C++ Group

|           | *HPP-FCL* | Jolt | libccd  | Bullet |
|-----------|-----------|------|---------|--------|
| *HPP-FCL* |           | 0.47 | 0.41    | 0.20   |
| Jolt      | ns        |      | 0.44    | 0.21   |
| libccd    | ns        | ns   |         | 0.26   |
| Bullet    | ns        | ns   | ns      |        |

#### Rust Group

|            | *ncollide* | c-rs nest | c-rs dist | c-rs inter | gjk-rs |
|------------|------------|-----------|-----------|------------|--------|
| *ncollide* |            | 0.04      | 0.16      | 0.47       | ns     |
| c-rs nest  | ns         |           | ns        | ns         | ns     |
| c-rs dist  | ns         | 0.17      |           | ns         | ns     |
| c-rs inter | ns         | 0.00      | 0.07      |            | 0.49   |
| gjk-rs     | ns         | 0.10      | 0.24      | ns         |        |

#### Python Group

|                         | *PyBullet* | d3d tuple acc | d3d tuple no acc | d3d nest acc | d3d nest no acc | d3d jolt dist | d3d jolt inter | d3d org |
|-------------------------|------------|---------------|------------------|--------------|-----------------|---------------|----------------|---------|
| *PyBullet*              |            | 0.14          | 0.00             | 0.00         | 0.00            | 0.00          | 0.00           | 0.00    |
| distance3d tuple acc    | ns         |               | 0.00             | 0.00         | 0.00            | 0.00          | 0.00           | 0.00    |
| distance3d tuple no acc | ns         | ns            |                  | ns           | 0.35            | 0.45          | ns             | ns      |
| distance3d nest acc     | ns         | ns            | 0.42             |              | 0.12            | 0.37          | ns             | 0.39    |
| distance3d nest no acc  | ns         | ns            | ns               | ns           |                 | ns            | ns             | ns      |
| distance3d jolt dist    | ns         | ns            | ns               | ns           | 0.37            |               | ns             | ns      |
| distance3d jolt inter   | ns         | ns            | 0.38             | 0.45         | 0.24            | 0.33          |                | 0.43    |
| distance3d org          | ns         | ns            | 0.44             | ns           | 0.14            | 0.40          | ns             |         |

### Results on PC2

Results of hypothesis testing for time per collision test *on PC2*.

#### C++ Group

| | HPP-FCL | *Jolt* | libccd | Bullet |
|-|-|-|-|-|
| HPP-FCL | |ns |0.47 |0.24 |
| *Jolt* |0.35 | |0.32 |0.14 |
| libccd |ns |ns | |0.26 |
| Bullet |ns |ns |ns | |

#### Rust Group

| | ncollide | c-rs nest | c-rs dist | c-rs inter | *gjk-rs* |
|-|-|-|-|-|-|
| ncollide | |0.04 |0.18 |ns |ns |
| c-rs nest |ns | |ns |ns |ns |
| c-rs dist |ns |0.17 | |ns |ns |
| c-rs inter |ns |0.01 |0.08 | |0.49 |
| *gjk-rs* |0.47 |0.10 |0.24 |ns | |

#### Python Group

| | *PyBullet* | d3d tuple acc | d3d tuple no acc | d3d nest acc | d3d nest no acc | d3d jolt dist | d3d jolt inter | d3d org |
|-|-|-|-|-|-|-|-|-|
| *PyBullet* | |0.14 |0.00 |0.00 |0.00 |0.00 |0.00 |0.00 |
| distance3d tuple acc |ns | |0.00 |0.00 |0.00 |0.00 |0.00 |0.00 |
| distance3d tuple no acc |ns |ns | |0.49 |0.33 |0.47 |ns |ns |
| distance3d nest acc |ns |ns |ns | |0.18 |ns |ns |ns |
| distance3d nest no acc |ns |ns |ns |ns | |ns |ns |ns |
| distance3d jolt dist |ns |ns |ns |ns |0.32 | |ns |ns |
| distance3d jolt inter |ns |ns |0.38 |0.35 |0.20 |0.34 | |0.36 |
| distance3d org |ns |ns |0.49 |0.46 |0.14 |0.48 |ns | |

## Folder-Structure
- [compare-cpp/README](./compare-cpp/README.md)
- [compare-rs/README](./compare-rs/README.md)
- [compare-python/README](./compare-python/README.md)
- [scripts/README](./scripts/README.md)

## Setup

### Quickstart
#### 1. Build and enter the docker container:
```bash
docker buildx build -t compare .
docker run --mount type=bind,source=".",target="/collision-comparison" --rm -it --entrypoint bash compare
```

#### 2. Generate additional benchmark case files
Since the case files for the "icospheres_of_different_high_vertex_counts" benchmark are too 
large to push to GitHub (~500MiB uncompressed), generate them locally using the python environment inside the container:
```bash
cd /collision-comparison
export PYTHONPATH="${PYTHONPATH}:collision-comparison/compare-python"
cd compare-python
python3 test_file/from_icospheres_of_different_high_vertex_counts.py
```

#### 3. Run the benchmarks
Run all benchmarks inside the container (This will take approx. 48h to complete).
The script will take care of downloading additional dependencies, 
unpacking the benchmark data, compiling the C++ benchmarking code, 
running the benchmarks and compiling the results into CSV files:
```bash
cd /collision-comparison
bash scripts/setup_repo_and_start_all_benchmarks.sh 
```

### Starting only specific benchmarks
To run only specific benchmarks, take a look at `scripts/setup_repo_and_start_all_benchmarks.sh` 
and comment out unwanted benchmarks, or run the scripts in `scripts/benchmarks` directly.

## Results 
### How many Folders are done?
```bash
cd results
tree -L 1 | tail -1
```

### Analyzing Results
The CSV files generated during the previous step can be used in the evaluation notebooks located in `compare-python/analyze_new`.
Every row in a CSV file contains the mean time per collision query for every algorithm, for that case file.

### Result Dataset 
A zip Archive of all the recorded data is saved in the dfki Fileserver at the path: `Research/projects/ongoing/APRIL_FK_21170/documentation/experiments`





## Funding

This project has been developed initially at the Robotics Innovation Center
of the German Research Center for Artificial Intelligence (DFKI GmbH) in
Bremen. At this phase the work was supported through a grant from the European
Commission (870142).

<img src="doc/DFKI_RIC_RGB.png" height="100px" />
