
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

using hpp::fcl::Vec3f;
using hpp::fcl::Triangle;

using hpp::fcl::details::MinkowskiDiff;

namespace compare::FCL {
    struct FCLCollider {
        Vec3f* vertices;
        Triangle* triangles;

        ShapeBase* shape;
    };

    struct FCLCase{
        FCLCollider collider0;
        FCLCollider collider1;

        MinkowskiDiff mink_diff;
    };


    void get_cases(Case* base_cases, FCLCase* fcl_cases, int length, bool force_linear_support_func);
    float get_distance_nesterov(FCLCase& fcl_case);
    bool get_intersection_nesterov(FCLCase& fcl_case);

    float get_distance_default(FCLCase& fcl_case);
    bool get_intersection_default(FCLCase& fcl_case);
}


