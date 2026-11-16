#pragma once

// Coal (formerly HPP-FCL, https://github.com/coal-library/coal, devel branch pinned in scripts/repo_setup.sh): GJK with the
// variants of Montaut et al.: vanilla GJK, Nesterov acceleration (RSS 2022) with and without normalized support
// directions, and Polyak acceleration (GJK++, T-RO 2024).

#include "collider.h"

#include <coal/narrowphase/gjk.h>
#include <coal/narrowphase/minkowski_difference.h>
#include <coal/shape/convex.h>
#include <coal/shape/geometric_shapes.h>

using compare::Base::Collider;
using compare::Base::Case;
using compare::Base::SupportMode;

namespace compare::FCL {
    struct FCLCollider {
        coal::ShapeBase* shape;
    };

    struct FCLCase{
        FCLCollider collider0;
        FCLCollider collider1;

        coal::details::MinkowskiDiff mink_diff;
    };

    void get_cases(Case* base_cases, FCLCase* fcl_cases, int length, SupportMode support_mode);

    // vanilla GJK
    float get_distance_default(FCLCase& fcl_case);
    bool get_intersection_default(FCLCase& fcl_case);

    // Nesterov acceleration without normalized support directions (Montaut et al., RSS 2022)
    float get_distance_nesterov(FCLCase& fcl_case);
    bool get_intersection_nesterov(FCLCase& fcl_case);

    // Nesterov acceleration with normalized support directions (Montaut et al., T-RO 2024, Alg. 7)
    float get_distance_nesterov_normalized(FCLCase& fcl_case);
    bool get_intersection_nesterov_normalized(FCLCase& fcl_case);

    // Polyak acceleration (Montaut et al., T-RO 2024)
    float get_distance_polyak(FCLCase& fcl_case);
    bool get_intersection_polyak(FCLCase& fcl_case);
}
