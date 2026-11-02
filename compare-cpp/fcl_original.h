#pragma once

// The original FCL (flexible-collision-library) with its own GJK (solver type GST_INDEP), not the GJK of libccd
// that FCL uses by default and not the fork HPP-FCL (see fcl.h).

#include "collider.h"

#include <memory>

#include <fcl/geometry/shape/shape_base.h>
#include <fcl/narrowphase/detail/convexity_based_algorithm/minkowski_diff.h>

using compare::Base::Case;

namespace compare::FCLOriginal {
    struct FCLOriginalCase {
        std::shared_ptr<fcl::ShapeBased> shape0;
        std::shared_ptr<fcl::ShapeBased> shape1;

        fcl::detail::MinkowskiDiffd mink_diff;
    };

    void get_cases(Case* base_cases, FCLOriginalCase* fcl_cases, int length);
    float get_distance(FCLOriginalCase& fcl_case);
}
