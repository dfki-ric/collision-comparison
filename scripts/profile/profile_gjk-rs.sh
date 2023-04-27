#!/bin/bash
cd gjk-rs

cargo build --bin profile_gjk
perf record --call-graph dwarf target/debug/profile_gjk
hotspot ./perf.data