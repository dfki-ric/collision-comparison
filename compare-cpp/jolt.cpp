#include "jolt.h"
#include "Jolt/Physics/Character/CharacterVirtual.h"

#include <iostream>

#include <Jolt/Jolt.h>

#include <Jolt/Core/JobSystemThreadPool.h>
#include <Jolt/Physics/PhysicsSystem.h>
#include <Jolt/Physics/Body/BodyCreationSettings.h>
#include <Jolt/Physics/Body/BodyActivationListener.h>
#include <Jolt/Physics/Collision/CollideShape.h>
#include <Jolt/Physics/Collision/Shape/ConvexHullShape.h>
#include <Jolt/Geometry/GJKClosestPoint.h>
#include <Jolt/Physics/Collision/CollisionDispatch.h>
#include <Jolt/RegisterTypes.h>
#include <Jolt/Core/Factory.h>


using JPH::SubShapeIDCreator;
using JPH::CollideShapeSettings;
using JPH::GJKClosestPoint;
using JPH::TransformedConvexObject;
using JPH::Array;

namespace compare::Jolt {

    void init(){
        JPH::RegisterDefaultAllocator();

        // Create a factory
        JPH::Factory::sInstance = new JPH::Factory();

        // Register all Jolt physics types
        JPH::RegisterTypes();

        // We need a temp allocator for temporary allocations during the physics update. We're
        // pre-allocating 10 MB to avoid having to do allocations during the physics update.
        // B.t.w. 10 MB is way too much for this example but it is a typical value you can use.
        // If you don't want to pre-allocate you can also use TempAllocatorMalloc to fall back to
        // malloc / free.
        JPH::TempAllocatorImpl temp_allocator(10 * 1024 * 1024);
    }

    Mat44 get_transform(Collider collider){
        return Mat44(JPH::Vec4(collider.colliderToOrigen[0][0], collider.colliderToOrigen[1][0], collider.colliderToOrigen[2][0], collider.colliderToOrigen[3][0]),
                     JPH::Vec4(collider.colliderToOrigen[0][1], collider.colliderToOrigen[1][1], collider.colliderToOrigen[2][1], collider.colliderToOrigen[3][1]),
                     JPH::Vec4(collider.colliderToOrigen[0][2], collider.colliderToOrigen[1][2], collider.colliderToOrigen[2][2], collider.colliderToOrigen[3][2]),
                     JPH::Vec4(collider.colliderToOrigen[0][3], collider.colliderToOrigen[1][3], collider.colliderToOrigen[2][3], collider.colliderToOrigen[3][3]));
    }

    void get_collider(Collider collider, JoltCollider& jolt_collider){
        if (collider.type == ColliderType::Sphere){
            auto sphere = new SphereShape(get_radius(collider));
            jolt_collider.shape = sphere;
        }

        if (collider.type == ColliderType::Cylinder){
            auto cylinder = new CylinderShape(get_height(collider) / 2, get_radius(collider), JPH::min(get_height(collider) / 2, get_radius(collider)));
            jolt_collider.shape = cylinder;
        }

        if (collider.type == ColliderType::Capsule){
            auto capsule = new CapsuleShape(get_height(collider) / 2, get_radius(collider));
            jolt_collider.shape = capsule;
        }

        if (collider.type == ColliderType::Box){
            auto box = new BoxShape(JPH::Vec3(get_size_x(collider) / 2, get_size_y(collider) / 2, get_size_z(collider) / 2),
                                          JPH::min(get_size_x(collider) / 2, JPH::min(get_size_y(collider) / 2, get_size_z(collider) / 2)));
            jolt_collider.shape = box;
        }

        if (collider.type == ColliderType::Mesh){
            unsigned int vertex_count = get_vertex_count(collider);
            for (int i = 0; i < vertex_count; i++){
                auto vertex = JPH::Vec3(collider.vertecies[i].x, collider.vertecies[i].y, collider.vertecies[i].z);
                jolt_collider.vertexList.push_back(vertex);
            }

            auto mesh_settings = JPH::ConvexHullShapeSettings(jolt_collider.vertexList);
            // increase resolution of the hull (=number of points inside the hull) as much as possible
            // also keep in mind that jolt automatically simplifies all meshes to a maximum of 256 vertices
            // when converting to a convex hull
            mesh_settings.mHullTolerance = 1e-10;
            auto result = new JPH::Shape::ShapeResult();
            auto mesh = new JPH::ConvexHullShape(mesh_settings, *result);

            if (result->HasError()) { std::cerr << result->GetError() << std::endl;}
            jolt_collider.shape = mesh;

        }
    }

    void get_case(Collider collider0, Collider collider1, JoltCase& jolt_case){

        jolt_case.transform0 = get_transform(collider0);
        jolt_case.transform1 = get_transform(collider1);

        get_collider(collider0, jolt_case.collider0);
        get_collider(collider1, jolt_case.collider1);
    }

    
    void get_cases(Case* base_cases, JoltCase* jolt_cases, int length){
        for (int i = 0; i < length; i++) {
            get_case(base_cases[i].collider0, base_cases[i].collider1, jolt_cases[i]);
        }
    }


    bool get_intersection(JoltCase& jolt_case){
        GJKClosestPoint closestPoint;
        JPH::Vec3 initialSeparatingAxis(0,0,0);

        auto supportMode = JPH::ConvexShape::ESupportMode::ExcludeConvexRadius;
        auto buffer0 = JPH::ConvexShape::SupportBuffer();
        auto buffer1 = JPH::ConvexShape::SupportBuffer();
        auto scale = JPH::Vec3(1,1,1);
        auto collider0_support = jolt_case.collider0.shape->GetSupportFunction(supportMode, buffer0, scale);
        auto collider1_support = jolt_case.collider1.shape->GetSupportFunction(supportMode, buffer1, scale);

        // Bring collider1 into collider0's local space:
        Mat44 transform_1_to_0 = jolt_case.transform0.InversedRotationTranslation() * jolt_case.transform1;
        TransformedConvexObject transformed1(transform_1_to_0, *collider1_support);

        return closestPoint.Intersects(*collider0_support, transformed1, 0.000001f, initialSeparatingAxis);
    }

    float get_distance(JoltCase& jolt_case){
        GJKClosestPoint closestPoint;
        JPH::Vec3 initialSeparatingAxis(0,0,0);

        auto supportMode = JPH::ConvexShape::ESupportMode::ExcludeConvexRadius;
        auto buffer0 = JPH::ConvexShape::SupportBuffer();
        auto buffer1 = JPH::ConvexShape::SupportBuffer();
        auto scale = JPH::Vec3(1,1,1);
        auto collider0_support = jolt_case.collider0.shape->GetSupportFunction(supportMode, buffer0, scale);
        auto collider1_support = jolt_case.collider1.shape->GetSupportFunction(supportMode, buffer1, scale);
        JPH::Vec3 outPointA;
        JPH::Vec3 outPointB;

        // Bring collider1 into collider0's local space:
        Mat44 transform_1_to_0 = jolt_case.transform0.InversedRotationTranslation() * jolt_case.transform1;
        TransformedConvexObject transformed1(transform_1_to_0, *collider1_support);

        float dist_squared = closestPoint.GetClosestPoints(
            *collider0_support, transformed1,
            0.000001f, 100.0f,
            initialSeparatingAxis,
            outPointA, outPointB
            );

        return JPH::sqrt(dist_squared);
    }
}


