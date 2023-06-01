

## Setup
```bash
# distance3d
git clone git@github.com:MaartenBehn/distance3d.git
cd distance3d/
git checkout feature/accelerated_GJK
python3 -m pip install -e .
cd ..

# collision-rs
git clone git@github.com:MaartenBehn/collision-rs.git

# gjk-rs
git clone git@github.com:MaartenBehn/gjk-rs.git

# fcl
git clone git@github.com:MaartenBehn/hpp-fcl.git

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
git clone git@github.com:google/benchmark.git
```

Rust nightly is needed: 
```bash
rustup toolchain install nightly
```

## Dependencies
- octomap
- assimp
- eigen