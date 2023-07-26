from test_file_creater.analyze import analyze_robot
from test_file_creater.load_nao import get_nao_bvh

tm, bvh = get_nao_bvh()
analyze_robot(bvh)
