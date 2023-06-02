#include "jolt.h"

#include <iostream>

#include <Jolt/Jolt.h>

#include <Jolt/Core/JobSystemThreadPool.h>
#include <Jolt/Physics/PhysicsSystem.h>
#include <Jolt/Physics/Body/BodyCreationSettings.h>
#include <Jolt/Physics/Body/BodyActivationListener.h>
#include <Jolt/Physics/Collision/CollideShape.h>
#include <Jolt/Geometry/GJKClosestPoint.h>
#include <Jolt/Geometry/ConvexSupport.h>

using JPH::GJKClosestPoint;
using JPH::TransformedConvexObject;

namespace compare::Jolt {

    Mat44 get_transform(Collider collider){
        return Mat44(JPH::Vec4(collider.colliderToOrigen[0], collider.colliderToOrigen[4], collider.colliderToOrigen[8], collider.colliderToOrigen[12]),
                     JPH::Vec4(collider.colliderToOrigen[1], collider.colliderToOrigen[5], collider.colliderToOrigen[9], collider.colliderToOrigen[13]),
                     JPH::Vec4(collider.colliderToOrigen[2], collider.colliderToOrigen[6], collider.colliderToOrigen[10], collider.colliderToOrigen[14]),
                     JPH::Vec4(collider.colliderToOrigen[3], collider.colliderToOrigen[7], collider.colliderToOrigen[11], collider.colliderToOrigen[15]));
    }

    void get_collider(Collider collider, JoltCollider* jolt_collider){
        if (collider.type == ColliderType::Sphere){
            auto sphere = SphereShape(get_radius(collider));
            jolt_collider->support = sphere.GetSupportFunction(JPH::ConvexShape::ESupportMode::ExcludeConvexRadius, jolt_collider->supportBuffer, JPH::Vec3::sReplicate(1.0f));
        }

        if (collider.type == ColliderType::Cylinder){
            auto cylinder = CylinderShape(get_height(collider) / 2, get_radius(collider), JPH::min(get_height(collider) / 2, get_radius(collider)));
            jolt_collider->support = cylinder.GetSupportFunction(JPH::ConvexShape::ESupportMode::ExcludeConvexRadius, jolt_collider->supportBuffer, JPH::Vec3::sReplicate(1.0f));

        }

        if (collider.type == ColliderType::Capsule){
            auto capsule = CapsuleShape(get_height(collider) / 2, get_radius(collider));
            jolt_collider->support = capsule.GetSupportFunction(JPH::ConvexShape::ESupportMode::ExcludeConvexRadius, jolt_collider->supportBuffer, JPH::Vec3::sReplicate(1.0f));
        }

        if (collider.type == ColliderType::Box){
            auto box = BoxShape(JPH::Vec3(get_size_x(collider) / 2, get_size_y(collider) / 2, get_size_z(collider) / 2),
                                          JPH::min(get_size_x(collider) / 2, JPH::min(get_size_y(collider) / 2, get_size_z(collider) / 2)));

            jolt_collider->support = box.GetSupportFunction(JPH::ConvexShape::ESupportMode::ExcludeConvexRadius, jolt_collider->supportBuffer, JPH::Vec3::sReplicate(1.0f));

        }
    }

    void get_case(Collider collider0, Collider collider1, JoltCase* jolt_case){

        jolt_case->transform0 = get_transform(collider0);
        jolt_case->transform1 = get_transform(collider1);

        get_collider(collider0, &jolt_case->collider0);
        get_collider(collider1, &jolt_case->collider1);

    }


    void get_cases(Case* base_cases, JoltCase* jolt_cases, int length){

        for (int i = 0; i < length; i++) {
            auto base_case = base_cases[i];
            get_case(base_case.collider0, base_case.collider1, &jolt_cases[i]);

        }
    }

    float get_distance(const JoltCase &jolt_case){

        GJKClosestPoint gjk;

        Mat44 inverse_transform0 = jolt_case.transform0.InversedRotationTranslation();
        Mat44 transform_1_to_0 = inverse_transform0 * jolt_case.transform1;
        TransformedConvexObject<JPH::ConvexShape::Support> support1(transform_1_to_0, *jolt_case.collider1.support);

        JPH::Vec3 pa, pb, v = JPH::Vec3::sZero();

        float d = sqrt(gjk.GetClosestPoints(
                *jolt_case.collider0.support,
                support1,
                1.0e-4f, FLT_MAX, v, pa, pb));

        return d;
    }

}
