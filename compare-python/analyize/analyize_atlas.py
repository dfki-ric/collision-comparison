from src.analyze import analyze_robot
from src.load_atlas import get_atlas_bvh

tm, bvh = get_atlas_bvh()
analyze_robot(bvh)
