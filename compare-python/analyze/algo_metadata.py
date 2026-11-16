from enum import Enum


class AlgoData:
    class Category(Enum):
        INTERSECTION = "Intersection"
        DISTANCE = "Distance"

    class Language(Enum):
        CPP = "C++"
        RUST = "Rust"
        PYTHON = "Python"

    def __init__(self, pretty_name: str, language: Language, category: Category):
        self.pretty_name = pretty_name
        self.pretty_name_full = pretty_name + (" [dist]" if category  == AlgoData.Category.DISTANCE else " [bool]")
        self.language = language
        self.category = category


# For every algorithm name as it appears in the raw benchmark result CSVs,
# returns an AlgoData object containing metadata
algo_metadata = {
    "Coal distance nesterov":                               AlgoData("Coal Nest.", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection nesterov":                           AlgoData("Coal Nest.", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal distance nesterov linear support":                AlgoData("Coal Nest. [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection nesterov linear support":            AlgoData("Coal Nest. [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal distance":                                        AlgoData("Coal", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection":                                    AlgoData("Coal", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal distance linear support":                         AlgoData("Coal [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection linear support":                     AlgoData("Coal [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Jolt intersection":                            AlgoData("Jolt", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Jolt distance":                                AlgoData("Jolt", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "libccd intersection":                          AlgoData("libccd", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "libccd intersection linear support":           AlgoData("libccd [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "HPP-FCL distance":                                     AlgoData("HPP-FCL", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "HPP-FCL distance cached extremes":                     AlgoData("HPP-FCL [extremes]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "HPP-FCL distance nesterov":                            AlgoData("HPP-FCL Nest.", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "HPP-FCL distance nesterov cached extremes":            AlgoData("HPP-FCL Nest. [extremes]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "HPP-FCL intersection":                                 AlgoData("HPP-FCL", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "HPP-FCL intersection cached extremes":                 AlgoData("HPP-FCL [extremes]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "HPP-FCL intersection nesterov":                        AlgoData("HPP-FCL Nest.", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "HPP-FCL intersection nesterov cached extremes":        AlgoData("HPP-FCL Nest. [extremes]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "HPP-FCL distance linear support":                      AlgoData("HPP-FCL [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "HPP-FCL distance nesterov linear support":             AlgoData("HPP-FCL Nest. [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "HPP-FCL intersection linear support":                  AlgoData("HPP-FCL [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "HPP-FCL intersection nesterov linear support":         AlgoData("HPP-FCL Nest. [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "FCL original distance":                                AlgoData("FCL", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "MuJoCo distance":                              AlgoData("MuJoCo", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "MuJoCo intersection":                          AlgoData("MuJoCo", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Bullet distance":                              AlgoData("Bullet", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "openGJK distance":                             AlgoData("OpenGJK", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "openGJK distance linear support":              AlgoData("OpenGJK [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "libccd intersection cached extremes":          AlgoData("libccd [extremes]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal distance nesterov cached extremes":               AlgoData("Coal Nest. [extremes]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection nesterov cached extremes":           AlgoData("Coal Nest. [extremes]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal distance cached extremes":                        AlgoData("Coal [extremes]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection cached extremes":                    AlgoData("Coal [extremes]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal distance polyak":                                 AlgoData("Coal Polyak", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection polyak":                             AlgoData("Coal Polyak", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal distance polyak linear support":                  AlgoData("Coal Polyak [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection polyak linear support":              AlgoData("Coal Polyak [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal distance polyak cached extremes":                 AlgoData("Coal Polyak [extremes]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection polyak cached extremes":             AlgoData("Coal Polyak [extremes]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal distance nesterov normalized":                    AlgoData("Coal Nest. norm.", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal distance nesterov normalized linear support":     AlgoData("Coal Nest. norm. [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal distance nesterov normalized cached extremes":    AlgoData("Coal Nest. norm. [extremes]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "Coal intersection nesterov normalized":                AlgoData("Coal Nest. norm.", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal intersection nesterov normalized linear support": AlgoData("Coal Nest. norm. [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Coal intersection nesterov normalized cached extremes":AlgoData("Coal Nest. norm. [extremes]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "MuJoCo distance linear support":               AlgoData("MuJoCo [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "MuJoCo intersection linear support":           AlgoData("MuJoCo [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "MuJoCo distance hill climbing":                AlgoData("MuJoCo [hill climbing]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "MuJoCo intersection hill climbing":            AlgoData("MuJoCo [hill climbing]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "openGJK distance cached extremes":             AlgoData("OpenGJK [extremes]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "libccd intersection adaptive support":         AlgoData("libccd", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "openGJK distance adaptive support":            AlgoData("OpenGJK", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),

    "ncollide_distance":            AlgoData("ncollide", AlgoData.Language.RUST, AlgoData.Category.DISTANCE),
    "collision-rs_nasterov_gjk":    AlgoData("collision-rs Nest.", AlgoData.Language.RUST, AlgoData.Category.DISTANCE),
    "collision-rs_distance_gjk":    AlgoData("collision-rs", AlgoData.Language.RUST, AlgoData.Category.DISTANCE),
    "collision-rs_intersect_gjk":   AlgoData("collision-rs", AlgoData.Language.RUST, AlgoData.Category.INTERSECTION),
    "gjk-rs_nasterov_gjk":          AlgoData("gjk-rs", AlgoData.Language.RUST, AlgoData.Category.DISTANCE),

    "Pybullet":                                 AlgoData("PyBullet", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
    "distance3d Nesterov (with acceleration)":  AlgoData("distance3d HPP-FCL Nest.", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
    "distance3d Nesterov":                      AlgoData("distance3d HPP-FCL", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
    "distance3d Jolt (intersection)":           AlgoData("distance3d Jolt", AlgoData.Language.PYTHON, AlgoData.Category.INTERSECTION),
    "distance3d Jolt (distance)":               AlgoData("distance3d Jolt", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
    "distance3d Original":                      AlgoData("distance3d Orig.", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
}