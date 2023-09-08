#!/bin/bash
cd compare-rs
rm -rf target/criterion

source "$HOME/.cargo/env"
cargo bench 
cd ..