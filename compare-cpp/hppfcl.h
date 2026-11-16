
#pragma once

// The HPP-FCL fork of the earlier benchmark runs (MaartenBehn/hpp-fcl@23a71b9 with the cached-extremes patch), built
// separately by scripts/repo_setup.sh, for the comparison with Coal (fcl.h) in the same benchmark binary.

#include "collider.h"

#include <hpp/fcl/shape/geometric_shapes.h>
#include <hpp/fcl/narrowphase/narrowphase.h>

using compare::Base::Collider;
using compare::Base::Case;
using compare::Base::SupportMode;

using hpp::fcl::Box;
using hpp::fcl::Capsule;
using hpp::fcl::Sphere;
using hpp::fcl::Cylinder;
using hpp::fcl::Transform3f;
using hpp::fcl::Triangle;
using hpp::fcl::Convex;
using hpp::fcl::ShapeBase;

using hpp::fcl::Vec3f;
using hpp::fcl::Triangle;

using hpp::fcl::details::MinkowskiDiff;

namespace compare::HPPFCL {
    struct HPPFCLCollider {
        Vec3f* vertices;
        Triangle* triangles;

        ShapeBase* shape;
    };

    struct HPPFCLCase{
        HPPFCLCollider collider0;
        HPPFCLCollider collider1;

        MinkowskiDiff mink_diff;
    };


    void get_cases(Case* base_cases, HPPFCLCase* fcl_cases, int length, SupportMode support_mode);
    float get_distance_nesterov(HPPFCLCase& fcl_case);
    bool get_intersection_nesterov(HPPFCLCase& fcl_case);

    float get_distance_default(HPPFCLCase& fcl_case);
    bool get_intersection_default(HPPFCLCase& fcl_case);
}


