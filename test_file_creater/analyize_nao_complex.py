from test_file_creater.analyze import analyze_robot
from test_file_creater.load_nao import get_nao_bvh_complex

tm, bvh = get_nao_bvh_complex()
analyze_robot(bvh)
