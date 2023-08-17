#!/bin/bash
cd compare-rs
source "$HOME/.cargo/env"
cargo bench
cd ..