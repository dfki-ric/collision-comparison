

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
cd ..

# Jolt
git clone git@github.com:MaartenBehn/JoltPhysics.git


# Bullet
git clone git@github.com:MaartenBehn/bullet3.git


# Compare
cd compare/
mkdir build_debug/
mkdir build_release/
mkdir include/
cd include/
git clone git@github.com:nlohmann/json.git
git clone git@github.com:martinus/nanobench.git
cd ../..


# Data
mkdir data/
cd data
mkdir urdfs
cd urdfs

# -- Getting the Nao URDF --
# This part is a bit hacky. We essently just want the urdf of the nao robot and its mesh files. 
# This is nomally setup with ros so I modifieyed the cmake files to not have i crash.
git clone git@github.com:ros-naoqi/nao_robot.git
git clone git@github.com:MaartenBehn/nao_meshes.git
cd nao_meshes
mkdir build
cd build
cmake ..
make ._meshes # Follow the installer just press enter and say yes
cd ../..

# -- Getting the Atlas URDF --
git clone git@github.com:team-vigir/vigir_atlas_common.git



cd ../..
```

Rust nightly is needed: 
```bash
rustup toolchain install nightly
```

## Dependencies
- octomap
- assimp
- eigen