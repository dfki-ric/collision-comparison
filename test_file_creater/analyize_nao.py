from test_file_creater.analyze import analyze_robot
from test_file_creater.load_nao import get_nao_bvh

data_path = "../data/urdfs/nao/"
tm, bvh = get_nao_bvh(data_path)
analyze_robot(bvh)
