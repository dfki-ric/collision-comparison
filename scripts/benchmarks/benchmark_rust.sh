#!/bin/bash
cd compare-rs
rm -rf target/criterion

source "$HOME/.cargo/env"
# --no-fail-fast: if one benchmark binary fails (e.g., collision-rs panics), still run the others
cargo bench --no-fail-fast
cd ..