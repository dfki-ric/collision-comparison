from test_file_creater.load_nao import get_nao_bvh_complex
import pytransform3d.visualizer as pv

data_path = "../data/urdfs/nao/"
tm, bvh = get_nao_bvh_complex(data_path)

fig = pv.figure()
for artist in bvh.get_artists():
    artist.add_artist(fig)

if "__file__" in globals():
    fig.show()
else:
    fig.save_image("__open3d_rendered_image.jpg")