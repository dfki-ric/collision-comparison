
#pragma once 

#include "collider.h"

#include <Jolt/Jolt.h>
#include <Jolt/Physics/Collision/Shape/SphereShape.h>
#include <Jolt/Physics/Collision/Shape/CapsuleShape.h>
#include <Jolt/Physics/Collision/Shape/CylinderShape.h>
#include <Jolt/Physics/Collision/Shape/BoxShape.h>
#include <Jolt/Physics/Collision/Shape/Shape.h>
#include <Jolt/Geometry/ConvexSupport.h>

using compare::Base::Collider;
using compare::Base::ColliderType;
using compare::Base::Case;

using JPH::SphereShape;
using JPH::CapsuleShape;
using JPH::CylinderShape;
using JPH::BoxShape;
using JPH::Shape;
using JPH::ConvexShapeSettings;
using JPH::TransformedConvexObject;

using JPH::Mat44;

namespace compare::Jolt {

    struct JoltCollider {
        JPH::ConvexShape::SupportBuffer supportBuffer;
        const JPH::ConvexShape::Support* support;
    };

    struct JoltCase {
        Mat44 transform0;
        Mat44 transform1;

        JoltCollider collider0;
        JoltCollider collider1;
    };

    void get_case(Collider collider0, Collider collider1, JoltCase* jolt_case);
    void get_cases(Case* base_cases, JoltCase* jolt_cases, int length);
    float get_distance(const JoltCase &jolt_case);
}







