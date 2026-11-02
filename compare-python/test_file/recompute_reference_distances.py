"""Recomputes the reference distances of existing case files from the colliders stored in them.

The reference distance has to be computed from the meshes that the case files point to. Before the fix of
clean_collider_name (src/test_file.py), the meshes of URDF links with several visuals (the hands of the dual-arm
robot) were stored in one file, so the stored reference distances were computed from other meshes than the ones in
the case files.

Usage (from compare-python/): python test_file/recompute_reference_distances.py ../data/<dataset> [...]
"""
import argparse
import json
from pathlib import Path

import numpy as np
from distance3d.gjk import gjk

from src.test_file import from_dict, signed_distance


def recompute(case_file: Path):
    """Recomputes the distances of a case file in place, returns the old and new distances."""
    with open(case_file) as f:
        cases = json.load(f)

    # mesh paths are relative to the data directory, the parent of the dataset directory
    data_path = case_file.parent.parent
    old, new = [], []
    for case in cases:
        collider0, _ = from_dict(case["collider1"], data_path)
        collider1, _ = from_dict(case["collider2"], data_path)
        distance, _, _, _ = gjk(collider0, collider1)
        old.append(case["distance"])
        new.append(distance)
        case["distance"] = distance
        if "signed_distance" in case:
            case["signed_distance"] = signed_distance(collider0, collider1)

    with open(case_file, "w") as f:
        json.dump(cases, f, indent=4)
    return old, new


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("datasets", nargs="+", help="directories with the case files <dataset>_<i>.json")
    args = parser.parse_args()

    for dataset in map(Path, args.datasets):
        old, new = [], []
        case_files = sorted(dataset.glob(f"{dataset.name}_*.json"))
        for case_file in case_files:
            o, n = recompute(case_file)
            old.extend(o)
            new.extend(n)
        old, new = np.array(old), np.array(new)
        change = np.abs(new - old)
        print(f"{dataset.name}: {len(case_files)} case files, {len(new)} pairs, "
              f"{np.count_nonzero(change > 1e-3)} changed by more than 1 mm (max. {change.max():.4f} m), "
              f"intersection status changed for {np.count_nonzero((old <= 0) != (new <= 0))} pairs")
