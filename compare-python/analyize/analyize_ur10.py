from src.analyze import analyze_robot
from src.load_ur10 import get_u10_bvh

tm, bvh = get_u10_bvh()
analyze_robot(bvh)
