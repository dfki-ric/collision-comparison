import os
import json
from pathlib import Path
import matplotlib.pyplot as plt
import miniball
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter

from src import load_test_file
from src.test_file import load_mesh_from_obj

# BENCHMARK_DIR = Path("../data/icospheres_of_different_high_vertex_counts")
BENCHMARK_DIR = Path("../data/complex_env_dual_arm_collision")

# approximate distance interval in which Nesterov Accelerated HPP-FCL beats the default variant:
DIST_INTERVAL = [-0.002, 0.05]

print("Showing metadata for benchmark", BENCHMARK_DIR)

distances = []
num_cases_in_distance_interval = 0

directory_contents = os.scandir(BENCHMARK_DIR)
for entry in directory_contents:
    if not entry.is_file(): continue

    with open(entry.path) as json_file:
        cases = json.load(json_file)

    for case in cases:
        distances.append(case["signed_distance"])
        # distances.append(case["collider1"]["mesh_path"])
        if DIST_INTERVAL[0] <= case["signed_distance"] <= DIST_INTERVAL[1]:
            num_cases_in_distance_interval += 1

print(f"Number of cases in distance interval {DIST_INTERVAL}: {num_cases_in_distance_interval}  = {(num_cases_in_distance_interval/len(distances))*100:.2f}%")
print(f"Number of cases (total): {len(distances)}")
# plt.scatter(distances, y=np.arange(len(distances)) // 40)

fig, ax = plt.subplots(tight_layout=True)
cmap = plt.colormaps["coolwarm"]
N, bins, patches = ax.hist(distances,
                           bins=75,
                           weights=np.full_like(distances, 1/len(distances)),
                           )
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
bin_colors = []
for i in range(len(bins)-1):
    bin_middle = (bins[i]+bins[i+1])/2.0
    bin_colors.append(0.9 if DIST_INTERVAL[0] <= bin_middle < DIST_INTERVAL[1] else 0.1)

for color, patch in zip(bin_colors, patches):
    patch.set_facecolor(color = cmap(color))

custom_lines = [
    Line2D([0], [0], color=cmap(0.9), lw=4),
    Line2D([0], [0], color=cmap(0.1), lw=4)
]

ax.legend(custom_lines, ['Nesterov Accelerated GJK\nis likely more performant',
                         'Vanilla GJK is likely\nmore performant'
                         ])

plt.title("Histogram of distance distribution")
plt.xlabel("Distance [m]")
plt.ylabel("Percentage")
plt.show()

meshes_path = Path(BENCHMARK_DIR, "meshes")

if meshes_path.exists():
    print("Calculating radii of enclosing spheres, number of vertices and number of faces for all meshes...")
    radii = []
    n_vertices = []
    n_faces = []
    mesh_names = []
    for mesh in os.listdir(meshes_path):
        verts, tris = load_mesh_from_obj(Path(meshes_path, mesh))

        vertices = np.asarray(verts, dtype=np.float64)
        c, r2 = miniball.get_bounding_ball(vertices, rng=np.random.default_rng(42))
        radius = np.sqrt(r2)
        radii.append(radius)
        mesh_names.append(mesh)
        n_vertices.append(len(verts))
        n_faces.append(len(tris))


    print(f"Median Radius: {np.median(radii):.4f}m")
    print(f"Minimum Radius: {np.min(radii):.4f}m in mesh: {mesh_names[np.argmin(radii)]}")
    print(f"Maximum Radius: {np.max(radii):.4f}m in mesh: {mesh_names[np.argmax(radii)]}")

    print(f"Median # of vertices: {np.median(n_vertices):.0f}")
    print(f"Minimum # of vertices: {np.min(n_vertices):.0f} in mesh: {mesh_names[np.argmin(n_vertices)]}")
    print(f"Maximum # of vertices: {np.max(n_vertices):.0f} in mesh: {mesh_names[np.argmax(n_vertices)]}")

    print(f"Median # of faces: {np.median(n_faces):.0f}")
    print(f"Minimum # of faces: {np.min(n_faces):.0f} in mesh: {mesh_names[np.argmin(n_faces)]}")
    print(f"Maximum # of faces: {np.max(n_faces):.0f} in mesh: {mesh_names[np.argmax(n_faces)]}")
