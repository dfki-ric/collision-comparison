from test_file_creater.load_atlas import get_atlas_bvh
import pytransform3d.visualizer as pv

tm, bvh = get_atlas_bvh()

fig = pv.figure()
for artist in bvh.get_artists():
    artist.add_artist(fig)

if "__file__" in globals():
    fig.show()
else:
    fig.save_image("__open3d_rendered_image.jpg")