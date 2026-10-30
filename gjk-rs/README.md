# gjk-rs
This is my own attempt to write a gjk collision libary. 
This was done to compare my own implementation against collisions libaries like Jolt and Bullet. 
Refer to https://github.com/MaartenBehn/collision-comparison for more information.

## Profile
```bash
perf record --call-graph dwarf target
hotspot ./perf.data
```
