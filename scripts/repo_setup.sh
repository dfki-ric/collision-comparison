#!/bin/bash
# Sets up the repository for the benchmarks. Run it from the repository root inside the Docker container,
# which provides the system packages and Python dependencies (see Dockerfile).
# It unpacks the benchmark data, downloads and builds the libraries, and compiles the C++ benchmark.
# It can be run again: data, repositories and builds that already exist are kept.

source /opt/miniconda/bin/activate collision_env

# stop at the first failing step
set -e

# Benchmark data

mkdir -p results

unzip_dataset() {
  local name=$1
  if [ -d "data/$name" ]; then
    return
  fi
  echo "Unzipping $name..."
  (cd data && unzip -q "$name.zip")
}

unzip_dataset uc1_ur10_collision
unzip_dataset uc2_ur10_collision
unzip_dataset uc5_ur10_collision
unzip_dataset uc6_ur10_collision
unzip_dataset complex_env_dual_arm_collision
unzip_dataset complex_env_dual_arm_collision_max256verts
unzip_dataset icospheres_of_different_vertex_counts
unzip_dataset icospheres_fixed_size_distance_sweep

# too large for GitHub, it has to be generated (see README.md)
if [ ! -d "data/icospheres_of_different_high_vertex_counts" ]; then
  echo "Note: data/icospheres_of_different_high_vertex_counts is missing, generate it with" \
       "compare-python/test_file/from_icospheres_of_different_high_vertex_counts.py"
fi

# Libraries and dependencies

clone() {
  local url=$1
  local dir
  dir=$(basename "$url" .git)
  if [ ! -d "$dir" ]; then
    git clone "$url"
  fi
}

# applies a patch (path relative to the repository root) to a cloned repository, unless it is already applied
apply_patch() {
  local dir=$1
  local patch=$PWD/$2
  if ! git -C "$dir" apply --reverse --check "$patch" 2> /dev/null; then
    git -C "$dir" apply "$patch"
  fi
}

# collision detection libraries (forks contain changes for the benchmark)
clone https://github.com/MaartenBehn/JoltPhysics.git
clone https://github.com/danfis/libccd.git
clone https://github.com/MaartenBehn/bullet3.git
clone https://github.com/MaartenBehn/hpp-fcl.git
# pinned: the patch adds cached extremes to its hill climbing (support function variant of the benchmark)
git -C hpp-fcl checkout -q 23a71b9
apply_patch hpp-fcl compare-cpp/patches/hpp-fcl-cached-extremes.patch
clone https://github.com/AlexanderFabisch/distance3d.git
# the original FCL with its own GJK, at the latest release
clone https://github.com/flexible-collision-library/fcl.git
git -C fcl checkout -q 0.7.0

# dependencies of the C++ benchmark
clone https://github.com/nlohmann/json.git
clone https://github.com/martinus/nanobench.git
clone https://github.com/g-truc/glm.git

# Build

# All C/C++ libraries are built with the same optimizations: instructions of the host CPU, fast math and link-time
# optimization. Jolt is built with g++ like the other libraries: under clang, Jolt enforces -ffp-model=precise.
OPT_FLAGS="-march=native -ffast-math -flto=auto"

(cd JoltPhysics/Build \
 && sh ./cmake_linux_clang_gcc.sh Distribution g++ -DCMAKE_CXX_FLAGS="$OPT_FLAGS" \
 && cd Linux_Distribution \
 && make -j "$(nproc)")

# libccd must be built in double precision: in single precision, its GJK misses most intersections of small meshes.
# It is linked statically.
(mkdir -p libccd/build \
 && cd libccd/build \
 && cmake -G "Unix Makefiles" -DENABLE_DOUBLE_PRECISION=ON -DBUILD_SHARED_LIBS=OFF \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS="$OPT_FLAGS" .. \
 && make -j "$(nproc)")

# FCL is linked statically, with libccd from above and without tests and OctoMap
(mkdir -p fcl/build \
 && cd fcl/build \
 && cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="$OPT_FLAGS -I$PWD/../../libccd/build/src" \
    -DFCL_STATIC_LIBRARY=ON -DFCL_WITH_OCTOMAP=OFF -DBUILD_TESTING=OFF \
    -DCCD_INCLUDE_DIR="$PWD/../../libccd/src" -DCCD_LIBRARY="$PWD/../../libccd/build/src/libccd.a" .. \
 && cmake --build . --target fcl -j "$(nproc)")

# HPP-FCL and Bullet are built together with the C++ benchmark (see compare-cpp/CMakeLists.txt)
(cd hpp-fcl && git submodule update --init)

# distance3d still uses np.row_stack, which was removed in numpy 2.5, so numpy is pinned to 2.4
pip install -e ./distance3d "numpy==2.4"

mkdir -p compare-cpp/build_release
bash scripts/compile/compile_compare_release.sh

# remove old Rust builds, the Rust benchmark builds everything again
rm -rf compare-rs/target
