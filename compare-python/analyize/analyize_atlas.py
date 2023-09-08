from src import analyze_robot, get_atlas_bvh

tm, bvh = get_atlas_bvh()
analyze_robot(bvh)
