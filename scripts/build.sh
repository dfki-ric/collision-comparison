# distance3d
git https://github.com/MaartenBehn/distance3d.git
cd distance3d/
cd ..

# collision-rs
git clone https://github.com/MaartenBehn/collision-rs.git

# gjk-rs
git clone https://github.com/MaartenBehn/gjk-rs.git

# fcl
git clone https://github.com/MaartenBehn/hpp-fcl.git
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
git clone https://github.com/MaartenBehn/JoltPhysics.git
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
git clone https://github.com/MaartenBehn/bullet3.git
# cd bullet3
# mkdir build
# cd build
# cmake -DUSE_DOUBLE_PRECISION=ON -DBT_USE_EGL=ON -DCMAKE_BUILD_TYPE=Release ..
# make -j 8
# cd ../..


# Libccd
git clone https://github.com/danfis/libccd.git
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
git clone git@github.com:g-truc/glm.git
cd ../..