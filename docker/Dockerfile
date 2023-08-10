FROM manjarolinux/build:latest

# collision-comparison
RUN git clone https://github.com/MaartenBehn/collision-comparison.git

## Python

# distance3d
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/distance3d.git

RUN cd collision-comparison/compare-python \ 
 && python3 -m venv venv/ \
 && ./venv/bin/pip install numpy

RUN cd collision-comparison \
 && sh scripts/benchmarks/benchmark_python.sh


## Rust

# collision-rs
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/collision-rs.git

# gjk-rs
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/gjk-rs.git

# Compare-rs
# Install Rust
RUN pacman -Syy --noconfirm --needed \
    curl \
    && rm -f /var/cache/pacman/pkg/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

RUN cd collision-comparison/compare-rs \
 && source "$HOME/.cargo/env" \
 && cargo build


## Cpp

RUN pacman -Syy --noconfirm --needed \
    eigen \
    boost \
    assimp \
    clang \
    && rm -f /var/cache/pacman/pkg/*

# form aur with yay
RUN useradd builduser -m                                     
RUN passwd -d builduser                                      
RUN printf 'builduser ALL=(ALL) ALL\n' | tee -a /etc/sudoers 
RUN sudo -u builduser bash -c 'cd ~ \
 && git clone https://aur.archlinux.org/yay.git \
 && cd yay && makepkg -si --noconfirm' 

RUN sudo -u builduser bash -c 'yay -Syy --noconfirm octomap' 

# fcl
# RUN cd collision-comparison \ 
#  && git clone https://github.com/MaartenBehn/hpp-fcl.git \
#  && cd hpp-fcl \
#  && git submodule update --init \
#  && mkdir build_release \
#  && cd build_release \ 
#  && cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_PYTHON_INTERFACE:BOOL=OFF .. \
#  && make -j 8

# Jolt
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/JoltPhysics.git \
 && cd JoltPhysics/Build \
 && sh ./cmake_linux_clang_gcc.sh Distribution \
 && cd Linux_Distribution \
 && make -j 8 && ./UnitTests 

# Bullet
RUN cd collision-comparison \ 
 && git clone https://github.com/MaartenBehn/bullet3.git

# Libccd
RUN cd collision-comparison \ 
 && git clone https://github.com/danfis/libccd.git \
 && cd libccd \
 && mkdir build && cd build \
 && cmake -G "Unix Makefiles" .. \
 && make 

# Compare-cpp
RUN cd collision-comparison/compare-cpp \
 && mkdir build_debug/ \
 && mkdir build_release/ \
 && cd include \
 && git clone https://github.com/nlohmann/json.git \
 && git clone https://github.com/martinus/nanobench.git \
 && git clone https://github.com/g-truc/glm.git 




