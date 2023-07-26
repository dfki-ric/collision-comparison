from test_file_creater.analyze import analyze_robot
from test_file_creater.load_ur10 import get_u10_bvh

tm, bvh = get_u10_bvh()
analyze_robot(bvh)
