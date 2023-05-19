
#pragma once

#include "collider.h"

#include <hpp/fcl/shape/geometric_shapes.h>
#include <hpp/fcl/narrowphase/narrowphase.h>

using compare::Base::Collider;
using compare::Base::Case;

using hpp::fcl::Box;
using hpp::fcl::Capsule;
using hpp::fcl::Sphere;
using hpp::fcl::Cylinder;
using hpp::fcl::Transform3f;
using hpp::fcl::ShapeBase;

using hpp::fcl::details::MinkowskiDiff;

namespace compare::FCL {
    struct FCLCollider {
        Sphere sphere;
        Capsule capsule;
        Cylinder cylinder;
        Box box;

        ShapeBase* shape;
    };

    struct FCLCase{
        MinkowskiDiff mink_diff;
    };

    void get_fcl_cases(Case* base_cases, FCLCase* fcl_cases, int length);

    float get_fcl_distance(const FCLCase& fcl_case);
}


