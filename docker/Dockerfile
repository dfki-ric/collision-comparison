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
# Jolt
RUN git clone https://github.com/MaartenBehn/JoltPhysics.git \
 && cd JoltPhysics/Build \
 && sh ./cmake_linux_clang_gcc.sh Distribution \
 && cd Linux_Distribution \
 && make -j 8 && ./UnitTests 

# Libccd
RUN git clone https://github.com/danfis/libccd.git \
 && cd libccd \
 && mkdir build && cd build \
 && cmake -G "Unix Makefiles" .. \
 && make 

# Bullet
RUN git clone https://github.com/MaartenBehn/bullet3.git

# Fcl
RUN git clone https://github.com/MaartenBehn/hpp-fcl.git \  
 && cd hpp-fcl \
 && git submodule update --init

# distance3d
RUN git clone https://github.com/MaartenBehn/distance3d.git

# collision-rs
RUN git clone https://github.com/MaartenBehn/collision-rs.git

# gjk-rs
RUN git clone https://github.com/MaartenBehn/gjk-rs.git

# --- Setup test enviroment ---

# collision-comparison
RUN git clone https://github.com/MaartenBehn/collision-comparison.git

# --- Compare-Python ---
RUN cd collision-comparison/compare-python \ 
 && python3.8 -m venv venv/ \
 && ./venv/bin/python3 -m pip install --upgrade pip 

# Install distance3d
RUN cd collision-comparison/compare-python \ 
 && ./venv/bin/pip install -e ../../distance3d 

ENV PYTHONPATH="${PYTHONPATH}:collision-comparison/compare-python"

# Run python benchmark once
 RUN cd collision-comparison \
 && sh scripts/benchmarks/benchmark_python.sh

# --- Compare-rs ---
# Run rust benchmark once
RUN cd collision-comparison \
 && source "$HOME/.cargo/env" \
 && sh scripts/benchmarks/benchmark_rust.sh

# --- Compare-cpp ---
RUN cd collision-comparison/compare-cpp \
 && mkdir build_release/ \
 && cd include \
 && git clone https://github.com/nlohmann/json.git \
 && git clone https://github.com/martinus/nanobench.git \
 && git clone https://github.com/g-truc/glm.git 

RUN cd collision-comparison/ \
 && sh scripts/compile/compile_compare_release.sh

