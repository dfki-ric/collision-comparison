from src import analyze_robot, get_ur10_tm, get_ur10_bvh_from_tm

tm = get_ur10_tm()
bvh = get_ur10_bvh_from_tm(tm)
analyze_robot(bvh)
