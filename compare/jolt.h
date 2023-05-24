
#pragma once 

#include "collider.h"

#include <Jolt/Jolt.h>
#include <Jolt/Physics/Collision/Shape/SphereShape.h>
#include <Jolt/Physics/Collision/Shape/CapsuleShape.h>
#include <Jolt/Physics/Collision/Shape/CylinderShape.h>
#include <Jolt/Physics/Collision/Shape/BoxShape.h>
#include <Jolt/Physics/Collision/Shape/Shape.h>

using compare::Base::ColliderType;

using JPH::SphereShape;
using JPH::CapsuleShape;
using JPH::CylinderShape;
using JPH::BoxShape;
using JPH::Shape;
using JPH::ConvexShapeSettings;

using JPH::Mat44;

namespace compare::Jolt {

    struct JoltCollider {
        SphereShape sphere;
        CapsuleShape capsule;
        CylinderShape cylinder;
        BoxShape box;

        Shape* shape;
    };

    struct JoltCase {
        Mat44 transform0;
        Mat44 transform1;

        JoltCollider collider0;
        JoltCollider collider1;
    };

}







