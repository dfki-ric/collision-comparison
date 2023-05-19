
#pragma once

#include "collider.h"

#include <hpp/fcl/shape/geometric_shapes.h>
#include <hpp/fcl/narrowphase/narrowphase.h>

using compare::Base::Collider;

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
        FCLCollider collider0;
        FCLCollider collider1;

        MinkowskiDiff mink_diff;
    };

    FCLCase get_fcl_case(Collider collider0, Collider collider1);
    float get_fcl_distance(const FCLCase& fcl_case);
}


