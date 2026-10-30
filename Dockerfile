FROM ubuntu:24.04

# --- Dependencies ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential\
    libeigen3-dev \
    libboost-all-dev \
    libassimp-dev \
    clang \
    ninja-build \
    curl \
    libglu1-mesa-dev \
    liboctomap-dev \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    cmake \
    make \
    libcmocka-dev \
    wget \
    unzip \
    zip \
    && rm -rf /var/lib/apt/lists/*

## Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# --- Long Libary Builds ---
RUN #mkdir collision-comparison

# Jolt
#RUN cd collision-comparison \
# && git clone https://github.com/MaartenBehn/JoltPhysics.git \
# && cd JoltPhysics \
# && git checkout No-broadphase \
# && cd Build \
# && sh ./cmake_linux_clang_gcc.sh Distribution \
# && cd Linux_Distribution \
# && make -j 8

# Libccd
#RUN cd collision-comparison \
# && git clone https://github.com/danfis/libccd.git \
# && cd libccd \
# && mkdir build && cd build \
# && cmake -G "Unix Makefiles" .. \
# && make

# Bullet
#RUN cd collision-comparison \
# && git clone https://github.com/MaartenBehn/bullet3.git

# Fcl
#RUN cd collision-comparison \
# && git clone https://github.com/MaartenBehn/hpp-fcl.git \
# && cd hpp-fcl \
# && git submodule update --init

# OpenGJK
#RUN git clone https://github.com/MattiaMontanari/openGJK.git \
# && cd openGJK \
# && cmake -E make_directory build \
# && cmake -E chdir build cmake -DCMAKE_BUILD_TYPE=Release -G Ninja .. \
# && cmake --build build


# Compare-cpp dependecies
#RUN cd collision-comparison \
# && git clone https://github.com/nlohmann/json.git \
# && git clone https://github.com/martinus/nanobench.git \
# && git clone https://github.com/g-truc/glm.git

# Install miniconda
RUN cd /tmp \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-py313_26.1.1-1-Linux-x86_64.sh \
    && bash ./Miniconda3-py313_26.1.1-1-Linux-x86_64.sh -b -p /opt/miniconda \
    && rm Miniconda3-py313_26.1.1-1-Linux-x86_64.sh

# Set up miniconda environment
SHELL ["/bin/bash", "-c"]
RUN source /opt/miniconda/bin/activate \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r \
    && conda create --name collision_env python=3.12 -y

# Activate the miniconda env when entering the container
RUN echo "source /opt/miniconda/bin/activate collision_env" >> ~/.bashrc

# distance3d
#RUN cd collision-comparison \
# && git clone https://github.com/MaartenBehn/distance3d.git

# Install distance3d
#RUN cd collision-comparison \
# && source /opt/miniconda/bin/activate collision_env \
# && pip install -e ./distance3d

# Install Pybullet and needed python dependencies
RUN source /opt/miniconda/bin/activate collision_env \
 && pip install pybullet open3d

# collision-rs
#RUN cd collision-comparison \
# && git clone https://github.com/MaartenBehn/collision-rs.git

# gjk-rs
#RUN cd collision-comparison \
# && git clone https://github.com/MaartenBehn/gjk-rs.git

# --- Copy folders ---
#ADD results collision-comparison/results
#ADD scripts collision-comparison/scripts
#ADD data collision-comparison/data

# --- Compare-cpp ---
#ADD compare-cpp collision-comparison/compare-cpp
#RUN rm -rf collision-comparison/compare-cpp/build_release

#RUN cd collision-comparison/compare-cpp \
# && mkdir build_release/

#RUN cd collision-comparison/ \
# && sh scripts/compile/compile_compare_release.sh


# --- Compare-Python ---
#ADD compare-python collision-comparison/compare-python

#ENV PYTHONPATH="${PYTHONPATH}:collision-comparison/compare-python"

# Run python benchmark once
#RUN cd collision-comparison \
# && sh scripts/benchmarks/benchmark_python.sh


# --- Compare-rs ---
#ADD compare-rs collision-comparison/compare-rs
#RUN rm -rf collision-comparison/compare-rs/target

# set the shell to bash instead of sh, else the "source" command will not work
SHELL ["/bin/bash", "-c"]

# Run rust benchmark once
#RUN cd collision-comparison \
# && source "$HOME/.cargo/env" \
# && sh scripts/benchmarks/benchmark_rust.sh

