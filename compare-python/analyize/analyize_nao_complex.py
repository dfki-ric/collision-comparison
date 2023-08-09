from src.analyze import analyze_robot
from src.load_nao import get_nao_bvh_complex

tm, bvh = get_nao_bvh_complex()
analyze_robot(bvh)
