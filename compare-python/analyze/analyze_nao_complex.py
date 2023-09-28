from src import analyze_robot, get_nao_bvh_complex

tm, bvh = get_nao_bvh_complex()
analyze_robot(bvh)
