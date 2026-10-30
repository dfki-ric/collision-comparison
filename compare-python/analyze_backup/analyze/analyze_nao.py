from src import analyze_robot, get_nao_bvh

tm, bvh = get_nao_bvh()
analyze_robot(bvh)
