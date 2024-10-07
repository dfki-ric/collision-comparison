import numpy as np
import pytransform3d.visualizer as pv

from src import get_uc5_bvh, get_ur10_tm, get_ur10_bvh_from_tm, uc5_ur10_offset, set_random_joints

uc5_tm, uc5_bvh = get_uc5_bvh()
ur10_tm = get_ur10_tm()
set_random_joints(ur10_tm)
ur10_bvh = get_ur10_bvh_from_tm(ur10_tm, base_frame2origin=uc5_ur10_offset)

fig = pv.figure()
for artist in uc5_bvh.get_artists():
    artist.add_artist(fig)

for artist in ur10_bvh.get_artists():
    artist.add_artist(fig)

if "__file__" in globals():
    fig.show()
else:
    fig.save_image("__open3d_rendered_image.jpg")
