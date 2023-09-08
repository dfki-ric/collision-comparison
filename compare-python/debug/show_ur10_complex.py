import pytransform3d.visualizer as pv

from src import get_u10_bvh_complex

tm, bvh = get_u10_bvh_complex()

fig = pv.figure()
for artist in bvh.get_artists():
    artist.add_artist(fig)

if "__file__" in globals():
    fig.show()
else:
    fig.save_image("__open3d_rendered_image.jpg")