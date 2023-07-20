from test_file_creater.analyze import analyze_robot
from test_file_creater.load_atlas import get_atlas_bvh

data_path = "../data/urdfs/atlas/"
tm, bvh = get_atlas_bvh(data_path)
analyze_robot(bvh)
