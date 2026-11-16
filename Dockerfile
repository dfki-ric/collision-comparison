# Environment for the benchmarks: system packages, Rust and a conda environment with the Python dependencies.
# The libraries themselves are downloaded and built by scripts/repo_setup.sh in the mounted repository (see README.md).
FROM ubuntu:24.04

# use bash, so that "source" works in RUN commands
SHELL ["/bin/bash", "-c"]

ARG DEBIAN_FRONTEND=noninteractive

# Build tools and libraries for the C++ benchmark (Coal needs Eigen, Boost and assimp, Bullet needs OpenGL headers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    clang \
    cmake \
    make \
    ninja-build \
    git \
    ca-certificates \
    curl \
    wget \
    unzip \
    zip \
    libeigen3-dev \
    libboost-all-dev \
    libassimp-dev \
    liboctomap-dev \
    libglu1-mesa-dev \
    # runtime dependencies of open3d:
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
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# the repository is mounted from the host and belongs to another user than root:
# allow git to work in it (e.g., for the submodules of Coal)
RUN git config --global --add safe.directory '*'

# Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Miniconda with the environment collision_env
RUN cd /tmp \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-py313_26.1.1-1-Linux-x86_64.sh \
    && bash ./Miniconda3-py313_26.1.1-1-Linux-x86_64.sh -b -p /opt/miniconda \
    && rm Miniconda3-py313_26.1.1-1-Linux-x86_64.sh
RUN source /opt/miniconda/bin/activate \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r \
    && conda create --name collision_env python=3.12 -y

# activate the environment when entering the container
RUN echo "source /opt/miniconda/bin/activate collision_env" >> ~/.bashrc

# Python dependencies (distance3d is installed from its repository by scripts/repo_setup.sh)
RUN source /opt/miniconda/bin/activate collision_env \
    && pip install pybullet open3d pandas
