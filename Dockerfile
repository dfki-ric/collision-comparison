FROM manjarolinux/build:latest

# --- Dependencies ---
## Pacman 
RUN pacman -Suy --noconfirm --needed \
    go \
    eigen \
    boost \
    assimp \
    clang \
    ninja \
    curl \
    glu \
    && rm -f /var/cache/pacman/pkg/*

## yay
RUN useradd builduser -m                                     
RUN passwd -d builduser                                      
RUN printf 'builduser ALL=(ALL) ALL\n' | tee -a /etc/sudoers 
RUN sudo -u builduser bash -c 'cd ~ \
 && git clone https://aur.archlinux.org/yay.git \
 && cd yay && makepkg -si --noconfirm' 

RUN sudo -u builduser bash -c 'yay -Syy --noconfirm octomap' 

## Install Python 3.8
RUN sudo -u builduser bash -c 'yay -Syy --noconfirm python38' 

## Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# --- Long Libary Builds ---
RUN mkdir collision-comparison

# Jolt
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/JoltPhysics.git \
 && cd JoltPhysics \
 && git checkout No-broadphase \
 && cd Build \
 && sh ./cmake_linux_clang_gcc.sh Distribution \
 && cd Linux_Distribution \
 && make -j 8

# Libccd
RUN cd collision-comparison \ 
 && git clone https://github.com/danfis/libccd.git \
 && cd libccd \
 && mkdir build && cd build \
 && cmake -G "Unix Makefiles" .. \
 && make 

# Bullet
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/bullet3.git

# Fcl
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/hpp-fcl.git \  
 && cd hpp-fcl \
 && git submodule update --init

# Compare-cpp dependecies
RUN cd collision-comparison \ 
 && git clone https://github.com/nlohmann/json.git \
 && git clone https://github.com/martinus/nanobench.git \
 && git clone https://github.com/g-truc/glm.git 

# Setup venv
RUN cd collision-comparison \ 
 && python3.8 -m venv venv/ \
 && ./venv/bin/python3 -m pip install --upgrade pip 

# distance3d
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/distance3d.git 

# Install distance3d
RUN cd collision-comparison \ 
 && ./venv/bin/pip install -e ./distance3d 

# Install Pybullet
RUN cd collision-comparison \ 
 && ./venv/bin/pip install pybullet

# collision-rs
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/collision-rs.git

# gjk-rs
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/gjk-rs.git

# --- Copy folders ---
ADD results collision-comparison/results
ADD scripts collision-comparison/scripts
ADD data collision-comparison/data

# --- Compare-cpp ---
ADD compare-cpp collision-comparison/compare-cpp
RUN rm -rf collision-comparison/compare-cpp/build_release

RUN cd collision-comparison/compare-cpp \
 && mkdir build_release/

RUN cd collision-comparison/ \
 && sh scripts/compile/compile_compare_release.sh


# --- Compare-Python ---
ADD compare-python collision-comparison/compare-python 

ENV PYTHONPATH="${PYTHONPATH}:collision-comparison/compare-python"

# Run python benchmark once
RUN cd collision-comparison \
 && sh scripts/benchmarks/benchmark_python.sh


# --- Compare-rs ---
ADD compare-rs collision-comparison/compare-rs 
RUN rm -rf collision-comparison/compare-rs/target

# Run rust benchmark once
RUN cd collision-comparison \
 && source "$HOME/.cargo/env" \
 && sh scripts/benchmarks/benchmark_rust.sh

