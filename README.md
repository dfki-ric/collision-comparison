
## Setup
```bash
# distance3d
git clone git@github.com:MaartenBehn/distance3d.git
cd distance3d/
git checkout feature/collider_to_dict
cd ..

# collision-rs
git clone git@github.com:MaartenBehn/collision-rs.git

# gjk-rs
git clone git@github.com:MaartenBehn/gjk-rs.git

# fcl
git clone git@github.com:MaartenBehn/hpp-fcl.git
cd hpp-fcl
git submodule update --init
## Debug
# mkdir build
# cd build
# cmake -DBUILD_PYTHON_INTERFACE:BOOL=OFF ..
# make -j 8
# cd ..
## Release
cd build_release
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_PYTHON_INTERFACE:BOOL=OFF ..
make -j 8
cd ../..

# Jolt
git clone git@github.com:MaartenBehn/JoltPhysics.git
cd JoltPhysics/Build
## Debug
# sh ./cmake_linux_clang_gcc.sh
# cd Linux_Debug
# make -j 8 && ./UnitTests
# cd ..
## Release
sh ./cmake_linux_clang_gcc.sh Distribution
cd Linux_Distribution
make -j 8 && ./UnitTests
cd ../..

# Bullet
git clone git@github.com:MaartenBehn/bullet3.git
# cd bullet3
# mkdir build
# cd build
# cmake -DUSE_DOUBLE_PRECISION=ON -DBT_USE_EGL=ON -DCMAKE_BUILD_TYPE=Release ..
# make -j 8
# cd ../..


# Libccd
git clone git@github.com:danfis/libccd.git
cd libccd
mkdir build && cd build
cmake -G "Unix Makefiles" ..
make
cd ..

# Compare
cd compare/
mkdir build_debug/
mkdir build_release/
mkdir include/
cd include/
git clone git@github.com:nlohmann/json.git
git clone git@github.com:martinus/nanobench.git
cd ../..
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

### Rust nightly is needed: 
```bash
rustup toolchain install nightly
```

### Dependencies
- octomap
- assimp
- eigen
