

## Setup
```bash
git clone git@github.com:MaartenBehn/distance3d.git
cd distance3d/
git checkout feature/accelerated_GJK
python3 -m pip install -e .
cd ..

git clone git@github.com:MaartenBehn/collision-rs.git

git clone git@github.com:MaartenBehn/gjk-rs.git

git clone git@github.com:MaartenBehn/hpp-fcl.git
cd hpp-fcl/
git submodule update --init
mkdir build
cd build/
cmake-gui .. # Disable Python
cmake ..
make -j12
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