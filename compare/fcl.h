
#pragma once

#include "collider.h"
#include "hpp/fcl/serialization/convex.h"

#include <hpp/fcl/shape/geometric_shapes.h>
#include <hpp/fcl/narrowphase/narrowphase.h>

using compare::Base::Collider;
using compare::Base::Case;

using hpp::fcl::Box;
using hpp::fcl::Capsule;
using hpp::fcl::Sphere;
using hpp::fcl::Cylinder;
using hpp::fcl::Transform3f;
using hpp::fcl::Triangle;
using hpp::fcl::Convex;
using hpp::fcl::ShapeBase;

using hpp::fcl::details::MinkowskiDiff;

namespace compare::FCL {
    struct FCLCollider {
        Sphere sphere;
        Capsule capsule;
        Cylinder cylinder;
        Box box;
        Convex<Triangle> convex;

        ShapeBase* shape;
    };

    struct FCLCase{
        FCLCollider collider0;
        FCLCollider collider1;

        MinkowskiDiff mink_diff;
    };

    FCLCase get_case(Collider collider0, Collider collider1);
    void get_cases(Case* base_cases, FCLCase* fcl_cases, int length);
    float get_distance(FCLCase* fcl_case);
}


