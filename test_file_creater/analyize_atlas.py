from test_file_creater.analyze import analyze_robot
from test_file_creater.load_atlas import get_atlas_bvh

tm, bvh = get_atlas_bvh()
analyze_robot(bvh)
