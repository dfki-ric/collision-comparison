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
    "FCL distance":                                 AlgoData("HPP-FCL Nest.", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "FCL intersection":                             AlgoData("HPP-FCL Nest.", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "FCL distance linear support":                  AlgoData("HPP-FCL Nest. [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "FCL intersection linear support":              AlgoData("HPP-FCL Nest. [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "FCL distance defaultGJK":                      AlgoData("HPP-FCL", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "FCL intersection defaultGJK":                  AlgoData("HPP-FCL", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "FCL distance defaultGJK linear support":       AlgoData("HPP-FCL [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "FCL intersection defaultGJK linear support":   AlgoData("HPP-FCL [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Jolt intersection":                            AlgoData("Jolt", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Jolt distance":                                AlgoData("Jolt", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "libccd intersection":                          AlgoData("libccd", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "libccd intersection linear support":           AlgoData("libccd [lin. support]", AlgoData.Language.CPP, AlgoData.Category.INTERSECTION),
    "Bullet distance":                              AlgoData("Bullet", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "openGJK distance":                             AlgoData("OpenGJK", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),
    "openGJK distance linear support":              AlgoData("OpenGJK [lin. support]", AlgoData.Language.CPP, AlgoData.Category.DISTANCE),

    "ncollide_distance":            AlgoData("ncollide", AlgoData.Language.RUST, AlgoData.Category.DISTANCE),
    "collision-rs_nasterov_gjk":    AlgoData("collision-rs Nesterov", AlgoData.Language.RUST, AlgoData.Category.DISTANCE),
    "collision-rs_distance_gjk":    AlgoData("collision-rs", AlgoData.Language.RUST, AlgoData.Category.DISTANCE),
    "collision-rs_intersect_gjk":   AlgoData("collision-rs", AlgoData.Language.RUST, AlgoData.Category.INTERSECTION),
    "gjk-rs_nasterov_gjk":          AlgoData("gjk-rs", AlgoData.Language.RUST, AlgoData.Category.DISTANCE),

    "Pybullet":                                 AlgoData("PyBullet", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
    "distance3d Nesterov (with acceleration)":  AlgoData("distance3d Nest. Acc.", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
    "distance3d Nesterov":                      AlgoData("distance3d Nest.", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
    "distance3d Jolt (intersection)":           AlgoData("distance3d Jolt", AlgoData.Language.PYTHON, AlgoData.Category.INTERSECTION),
    "distance3d Jolt (distance)":               AlgoData("distance3d Jolt", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
    "distance3d Original":                      AlgoData("distance3d Orig.", AlgoData.Language.PYTHON, AlgoData.Category.DISTANCE),
}