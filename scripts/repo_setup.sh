#!/bin/bash
source ~/.bashrc

source /opt/miniconda/bin/activate collision_env

# temporary: better move this to the Dockerfile
apt update -y
apt install -y unzip
pip install open3d
pip install pandas

# install open3d dependencies manually because this was causing problems before:
apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglx0 \
    libegl1 \
    libglu1-mesa \
    libgomp1 \
    libusb-1.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libglib2.0-0

mkdir -p results

if [ ! -d "data/complex_env_dual_arm_collision" ]; then
  echo "Unzipping main benchmark data..."
  cd data
  unzip -q complex_env_dual_arm_collision.zip
  cd ..
fi

if [ ! -d "data/complex_env_dual_arm_collision_max256verts" ]; then
  echo "Unzipping benchmark data for simplified meshes..."
  cd data
  unzip -q complex_env_dual_arm_collision_max256verts.zip
  cd ..
fi

if [ ! -d "data/icospheres_of_different_vertex_counts" ]; then
  echo "Unzipping benchmark data for icospheres of different vertex counts..."
  cd data
  unzip -q icospheres_of_different_vertex_counts.zip
  cd ..
fi

if [ ! -d "data/icospheres_of_different_high_vertex_counts" ]; then
  echo "Unzipping benchmark data for icospheres of high vertex counts..."
  cd data
  unzip -q icospheres_of_different_high_vertex_counts.zip
  cd ..
fi

if [ ! -d "data/uc1_ur10_collision" ]; then
  echo "Unzipping primitive benchmark data..."
  cd data
  unzip -q uc1_ur10_collision.zip
  cd ..
fi

if [ ! -d "data/icospheres_fixed_size_distance_sweep" ]; then
  echo "Unzipping benchmark data for icosphere distance sweep..."
  cd data
  unzip -q icospheres_fixed_size_distance_sweep.zip
  cd ..
fi


# Clone algorithms not already in repo:
git clone https://github.com/MaartenBehn/JoltPhysics.git
git clone https://github.com/danfis/libccd.git
git clone https://github.com/MaartenBehn/bullet3.git
git clone https://github.com/MaartenBehn/hpp-fcl.git

git clone https://github.com/AlexanderFabisch/distance3d.git

# Clone dependencies for the C++ part of the benchmarks:
git clone https://github.com/nlohmann/json.git
git clone https://github.com/martinus/nanobench.git
git clone https://github.com/g-truc/glm.git

# Compile algorithms:
cd JoltPhysics/Build \
 && sh ./cmake_linux_clang_gcc.sh Distribution \
 && cd Linux_Distribution \
 && make -j 8 \
 && cd ../../..
pwd
cd libccd \
 && mkdir -p build && cd build \
 && cmake -G "Unix Makefiles" .. \
 && make \
 && cd ../..

cd hpp-fcl \
 && git submodule update --init \
 && cd ..

cd openGJK \
 && cmake -E make_directory build \
 && cmake -E chdir build cmake -DCMAKE_BUILD_TYPE=Release -G Ninja .. \
 && cmake --build build \
 && cd ..

pip install -e ./distance3d

mkdir -p compare-cpp/build_release/ \
 && bash scripts/compile/compile_compare_release.sh

rm -rf compare-rs/target

# distance3d still uses np.row_stack, which was removed in numpy 2.5. As a workaround, pin the numpy version to 2.4:
pip install numpy==2.4
