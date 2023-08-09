from src.analyze import analyze_robot
from src.load_nao import get_nao_bvh

tm, bvh = get_nao_bvh()
analyze_robot(bvh)
