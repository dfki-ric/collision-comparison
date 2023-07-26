#include "jolt.h"
#include "Jolt/Physics/Character/CharacterVirtual.h"

#include <iostream>

#include <Jolt/Jolt.h>

#include <Jolt/Core/JobSystemThreadPool.h>
#include <Jolt/Physics/PhysicsSystem.h>
#include <Jolt/Physics/Body/BodyCreationSettings.h>
#include <Jolt/Physics/Body/BodyActivationListener.h>
#include <Jolt/Physics/Collision/CollideShape.h>
#include <Jolt/Physics/Collision/Shape/MeshShape.h>
#include <Jolt/Geometry/GJKClosestPoint.h>
#include <Jolt/Geometry/ConvexSupport.h>
#include <Jolt/Geometry/Sphere.h>
#include <Jolt/Physics/Collision/CollisionDispatch.h>
#include <Jolt/RegisterTypes.h>
#include <Jolt/Core/Factory.h>
#include <Jolt/Core/TempAllocator.h>
#include <Jolt/Core/JobSystemThreadPool.h>
#include <Jolt/Physics/PhysicsSettings.h>
#include <Jolt/Physics/PhysicsSystem.h>
#include <Jolt/Physics/Collision/Shape/BoxShape.h>
#include <Jolt/Physics/Collision/Shape/SphereShape.h>
#include <Jolt/Physics/Body/BodyCreationSettings.h>
#include <Jolt/Physics/Body/BodyActivationListener.h>

using JPH::GJKClosestPoint;
using JPH::TransformedConvexObject;

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
        return Mat44(JPH::Vec4(collider.colliderToOrigen[0], collider.colliderToOrigen[4], collider.colliderToOrigen[8], collider.colliderToOrigen[12]),
                     JPH::Vec4(collider.colliderToOrigen[1], collider.colliderToOrigen[5], collider.colliderToOrigen[9], collider.colliderToOrigen[13]),
                     JPH::Vec4(collider.colliderToOrigen[2], collider.colliderToOrigen[6], collider.colliderToOrigen[10], collider.colliderToOrigen[14]),
                     JPH::Vec4(collider.colliderToOrigen[3], collider.colliderToOrigen[7], collider.colliderToOrigen[11], collider.colliderToOrigen[15]));
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
                JPH::Float3 vertex = JPH::Float3(collider.vertecies[i].x, collider.vertecies[i].y, collider.vertecies[i].z);
                jolt_collider.vertexList.push_back(vertex);
            }


            unsigned int index_count = get_index_count(collider);
            unsigned int triangle_count = index_count / 3;
            JPH::IndexedTriangleList indexedTriangleList;
            for (int i = 0; i < triangle_count; i++){
                indexedTriangleList.emplace_back(collider.indicies[i * 3], collider.indicies[i * 3 + 1], collider.indicies[i * 3 + 2]);
            }

            auto mesh_settings = JPH::MeshShapeSettings(jolt_collider.vertexList, indexedTriangleList);
            auto result = new JPH::Shape::ShapeResult();
            auto mesh = new JPH::MeshShape(mesh_settings, *result);

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
            auto base_case = base_cases[i];
            get_case(base_case.collider0, base_case.collider1, jolt_cases[i]);

            get_distance(jolt_cases[i]);
        }
    }

    class Collector : public JPH::CollideShapeCollector {
    public:
        int hits;

        void AddHit(const ResultType &inResult){
            hits++;
        }
    };

    float get_distance(JoltCase& jolt_case){

        Collector collector = Collector();
        collector.hits = 0;
        JPH::CollideShapeSettings settings = JPH::CollideShapeSettings();
        JPH::SubShapeIDCreator part1, part2;
        JPH::CollisionDispatch::sCollideShapeVsShape(
                jolt_case.collider0.shape,
                jolt_case.collider1.shape,
                JPH::Vec3::sReplicate(1.0f),
                JPH::Vec3::sReplicate(1.0f),
                jolt_case.transform0, jolt_case.transform1,
                part1, part2, settings, collector);

        return 1.0f * (collector.hits == 0);
    }

}
