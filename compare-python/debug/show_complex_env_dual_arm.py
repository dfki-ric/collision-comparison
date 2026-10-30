import pytransform3d.visualizer as pv
import numpy as np
import matplotlib.pyplot as plt

from src import set_random_joints, complex_env_dual_arm_offset, get_complex_env_bvh, get_dual_arm_tm, \
    get_dual_arm_bvh_from_tm

use_visual_meshes = True
COLLISION_COLOR = [1.0, 0.0, 0.0]

complex_env_tm, complex_env_bvh = get_complex_env_bvh(use_visuals=use_visual_meshes)
dual_arm_tm = get_dual_arm_tm()

actuated_joints = []

for joint_name in dual_arm_tm._joints:
    limits = dual_arm_tm.get_joint_limits(joint_name)
    if limits[0] != limits[1]:
        actuated_joints.append(joint_name)

print(f"Number of actuated joints in the scene: {len(actuated_joints)}")
print(f"Joint names: {actuated_joints}")


dual_arm_bvh = get_dual_arm_bvh_from_tm(dual_arm_tm, base_frame2origin=complex_env_dual_arm_offset, use_visuals=use_visual_meshes)
colliding_pairs = []
# cycle through random poses until one has at least one collision
while len(colliding_pairs) < 1:
    # set_random_joints(dual_arm_tm)
    dual_arm_bvh = get_dual_arm_bvh_from_tm(dual_arm_tm, base_frame2origin=complex_env_dual_arm_offset, use_visuals=use_visual_meshes)
    colliding_pairs = complex_env_bvh.aabb_overlapping_with_other_bvh(dual_arm_bvh)


colliding_colliders = {}
pair_colors = plt.get_cmap("hsv")(np.linspace(0, 1, len(colliding_pairs), endpoint=False))[:, :3]

for pair_color, ((frame_a, collider_a), (frame_b, collider_b)) in zip(pair_colors, colliding_pairs):
    for collider in (collider_a, collider_b):
        if collider.artist_ is None:
            continue
        for geometry in collider.artist_.geometries:
            if hasattr(geometry, "paint_uniform_color"):
                geometry.paint_uniform_color(pair_color)



fig = pv.figure()

for artist in complex_env_bvh.get_artists():
    artist.add_artist(fig)

for artist in dual_arm_bvh.get_artists():
    artist.add_artist(fig)

if "__file__" in globals():
    fig.show()
else:
    fig.save_image("__open3d_rendered_image.jpg")
