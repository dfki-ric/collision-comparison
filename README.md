# Setup

## On Manjaro
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

## In Docker
```bash
docker buildx build -t compare .
docker run --mount type=bind,source="./results",target="/collision-comparison/results" --rm -it --entrypoint bash compare
```

## How many Folders?
```bash
tree -L 1 | tail -1
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

### Dependencies
- octomap
- assimp
- eigen
