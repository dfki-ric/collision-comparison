
# Benchmarking Collision Detection for Robotics

## Abstract
Collision detection in robotics plays an important role in simulation, planning, and control. In particular, Gilbert-Johnson-Keerthi (GJK) and its variants are still widely used. We are interested in the question of how much programming language, algorithm development, and implementation tricks influence the performance of this algorithm. We develop a benchmark that resembles how GJK is currently used in robotics and compare the performance of commonly used implementations of the algorithm. We analyse not just the moments of the distribution of measured times, but the whole distribution, which is relevant for real-time applications.
Surprisingly, we obtained the best performance with the Jolt game engine, which is usually not used in robotics and does not implement the latest algorithmic developments.
We also found that highly optimized C++ libraries are still faster than more recently developed Rust libraries and that Python cannot be used when performance is a constraint, even when highly optimized code is used.
However, statistical tests show that differences between the most commonly used C++ and Rust libraries are not significant.

## Results

<p float="left">
  <img src="doc/uc1_ur10_collision_on_UPLINX-4-U.png" width="400" />
  <img src="doc/uc6_ur10_collision_on_UPLINX-4-U.png" width="400" /> 
</p>

<p float="left">
  <img src="doc/uc6_ur10_collision_on_TEAM7-STUD-1B-U.png" width="400" />
</p>

## Setup

### In Docker
```bash
docker buildx build -t compare .
docker run --mount type=bind,source="./results",target="/collision-comparison/results" --rm -it --entrypoint bash compare
```

#### Run in docker
```bash
cd /collision-comparison
sh scripts/benchmarks/benchmark_uc6_ur10.sh 
# To run benchmark on uc6 with ur10
```

#### How many Folders are done?
```bash
cd results
tree -L 1 | tail -1
```

### On Manjaro
```bash
sudo pacman -Suy --noconfirm --needed \
    go \
    eigen \
    boost \
    assimp \
    clang \
    ninja \
    curl \
    glu

yay -Syy --noconfirm octomap

## Install Python 3.8
yay -Syy --noconfirm python38

## Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Jolt
git clone https://github.com/MaartenBehn/JoltPhysics.git \
 && cd JoltPhysics/Build \
 && sh ./cmake_linux_clang_gcc.sh Distribution \
 && cd Linux_Distribution \
 && make -j 8 && ./UnitTests \
 && cd ../../..

# Libccd
git clone https://github.com/danfis/libccd.git \
 && cd libccd \
 && mkdir build && cd build \
 && cmake -G "Unix Makefiles" .. \
 && make \
 && cd ../..

# Bullet
git clone https://github.com/MaartenBehn/bullet3.git

# Fcl
git clone https://github.com/MaartenBehn/hpp-fcl.git \  
 && cd hpp-fcl \
 && git submodule update --init \
 && cd ..

# Compare-cpp dependecies
git clone https://github.com/nlohmann/json.git \
 && git clone https://github.com/martinus/nanobench.git \
 && git clone https://github.com/g-truc/glm.git 

# Setup venv
python3.8 -m venv venv/ \
 && ./venv/bin/python3 -m pip install --upgrade pip 

# distance3d
git clone https://github.com/MaartenBehn/distance3d.git 

# Install distance3d
./venv/bin/pip install -e ./distance3d 

# Install Pybullet
./venv/bin/pip install pybullet

# collision-rs
git clone https://github.com/MaartenBehn/collision-rs.git

# gjk-rs
git clone https://github.com/MaartenBehn/gjk-rs.git

rm -rf collision-comparison/compare-cpp/build_release

cd compare-cpp \
 && mkdir build_release/ \
 && cd ..

sh scripts/compile/compile_compare_release.sh

# --- Compare-Python ---

# Run python benchmark once
export PYTHONPATH="${PYTHONPATH}:collision-comparison/compare-python" \
 && sh scripts/benchmarks/benchmark_python.sh

# --- Compare-rs ---
rm -rf collision-comparison/compare-rs/target

# Run rust benchmark once
source "$HOME/.cargo/env" \
 && sh scripts/benchmarks/benchmark_rust.sh
```





### Building URDFs (Not nessesary)
```bash
cd data/urdf

# Getting the Nao URDF:
# This part is a bit hacky. We essently just want the urdf of the nao robot and its mesh files. 
# This is nomally setup with ros so I modifieyed the cmake files to not have it crash.
cd nao
git clone git@github.com:ros-naoqi/nao_robot.git
git clone git@github.com:MaartenBehn/nao_meshes.git
cd nao_meshes
mkdir build
cd build
cmake ..
make ._meshes # Follow the installer just press enter and say yes
cd ../../..

# Getting the Atlas URDF:
cd atlas
git clone git@github.com:team-vigir/vigir_atlas_common.git
cd ..

# Getting the UR 10 and UR 5 URDF:
cd ur
git clone git@github.com:aprilprojecteu/april_robot_description.git
git clone git@github.com:ros-industrial/universal_robot.git
cd ../..
```

### If Rust nightly is needed: 
```bash
rustup toolchain install nightly
```
