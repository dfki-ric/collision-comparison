#!/usr/bin/env python3
"""
Randomly scatters objects around the "[left|right]_arm_base"
links of a URDF scene

Directory layout expected for the meshes:
    meshes/
        ycb-google_64k/
            object_name1/
                nontextured.stl
            object_name2/
                nontextured.stl
            ...
"""

import glob
import math
import os
import random
import re

arm_base_links = ["right_arm_base", "left_arm_base"]


def find_available_objects(meshes_root):
    pattern = os.path.join(meshes_root, "ycb-google_64k", "*", "nontextured.stl")
    matches = sorted(glob.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No mesh files found matching '{pattern}'. ")
    return [os.path.basename(os.path.dirname(m)) for m in matches]


def random_point_on_upper_hemisphere(radius):
    theta = random.uniform(0.0, 2.0 * math.pi)   # azimuth angle
    cos_phi = random.uniform(0.0, 1.0)        # elevation angle, restricted to upper half
    sin_phi = math.sqrt(1.0 - cos_phi ** 2)
    x = radius * sin_phi * math.cos(theta)
    y = radius * sin_phi * math.sin(theta)
    z = radius * cos_phi
    return x, y, z


def make_link_and_joint_xml(mesh_path_relative, link_name, joint_name, parent_link, xyz, rpy):
    xyz_str = "{:.5f} {:.5f} {:.5f}".format(*xyz)
    rpy_str = "{:.5f} {:.5f} {:.5f}".format(*rpy)
    return (
        f'  <link name="{link_name}">\n'
        f'    <collision>\n'
        f'      <origin rpy="0.00000 0.00000 0.00000" xyz="0.00000 0.00000 0.00000"/>\n'
        f'      <geometry>\n'
        f'        <mesh filename="{mesh_path_relative}"/>\n'
        f'      </geometry>\n'
        f'    </collision>\n'
        f'    <visual>\n'
        f'      <origin rpy="0.00000 0.00000 0.00000" xyz="0.00000 0.00000 0.00000"/>\n'
        f'      <geometry>\n'
        f'        <mesh filename="{mesh_path_relative}"/>\n'
        f'      </geometry>\n'
        f'      <material name="Grey"/>\n'
        f'    </visual>\n'
        f'  </link>\n'
        f'  <joint name="{joint_name}" type="fixed">\n'
        f'    <origin rpy="{rpy_str}" xyz="{xyz_str}"/>\n'
        f'    <parent link="{parent_link}"/>\n'
        f'    <child link="{link_name}"/>\n'
        f'  </joint>\n'
    )


def build_scene(urdf_text, meshes_root, num_objects, min_radius, max_radius):
    available_objects = find_available_objects(meshes_root)

    if num_objects > len(available_objects):
        chosen_objects = [random.choice(available_objects) for _ in range(num_objects)]
    else:
        chosen_objects = random.sample(available_objects, num_objects)

    used_link_names = set(re.findall(r'<link\s+name="([^"]+)"', urdf_text))
    new_blocks = []

    for i, object_name in enumerate(chosen_objects):
        parent_link = random.choice(arm_base_links)
        radius = random.uniform(min_radius, max_radius)
        xyz = random_point_on_upper_hemisphere(radius)
        rpy = [
            random.uniform(-math.pi, math.pi),
            random.uniform(-math.pi, math.pi),
            random.uniform(-math.pi, math.pi)
        ]

        link_name = f"{object_name}_{i}"
        suffix = 1
        while link_name in used_link_names:
            link_name = f"{object_name}_{i}_{suffix}"
            suffix += 1
        used_link_names.add(link_name)
        joint_name = f"{link_name}_joint"

        mesh_relative = f"meshes/ycb-google_64k/{object_name}/nontextured.stl"
        new_blocks.append(
            make_link_and_joint_xml(mesh_relative, link_name, joint_name, parent_link, xyz, rpy)
        )

    insertion_point = urdf_text.rfind("</robot>")
    if insertion_point == -1:
        raise ValueError("Could not find a closing '</robot>' tag in the URDF.")

    comment = "  <!-- Randomly placed objects -->\n"
    new_text = (
        urdf_text[:insertion_point]
        + comment
        + "".join(new_blocks)
        + urdf_text[insertion_point:]
    )
    return new_text, chosen_objects, arm_base_links


if __name__ == "__main__":
    input_urdf = "../data/urdfs/complex_env/complex_env.urdf"
    meshes_root = "../data/urdfs/complex_env/meshes"
    num_objects = 30
    min_radius = 0.4
    max_radius = 1.3
    # output_urdf = "../data/urdfs/complex_env/complex_env_with_objects.urdf"
    output_urdf = input_urdf

    random.seed(2)

    with open(input_urdf, "r") as f:
        urdf_text = f.read()

    new_text, chosen_objects, arm_base_links = build_scene(
        urdf_text,
        meshes_root,
        num_objects,
        min_radius,
        max_radius,
    )

    with open(output_urdf, "w") as f:
        f.write(new_text)

    print(f"Arm base links found: {arm_base_links}")
    print(f"Placed {len(chosen_objects)} objects: {chosen_objects}")
    print(f"Written to: {output_urdf}")


