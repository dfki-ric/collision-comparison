#include "jolt.h"

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

using JPH::GJKClosestPoint;
using JPH::TransformedConvexObject;

namespace compare::Jolt {

    Mat44 get_transform(Collider collider){
        return Mat44(JPH::Vec4(collider.colliderToOrigen[0], collider.colliderToOrigen[4], collider.colliderToOrigen[8], collider.colliderToOrigen[12]),
                     JPH::Vec4(collider.colliderToOrigen[1], collider.colliderToOrigen[5], collider.colliderToOrigen[9], collider.colliderToOrigen[13]),
                     JPH::Vec4(collider.colliderToOrigen[2], collider.colliderToOrigen[6], collider.colliderToOrigen[10], collider.colliderToOrigen[14]),
                     JPH::Vec4(collider.colliderToOrigen[3], collider.colliderToOrigen[7], collider.colliderToOrigen[11], collider.colliderToOrigen[15]));
    }

    void get_collider(Collider collider, JoltCollider& jolt_collider){
        if (collider.type == ColliderType::Sphere){
            auto sphere = SphereShape(get_radius(collider));
            jolt_collider.support = sphere.GetSupportFunction(JPH::ConvexShape::ESupportMode::ExcludeConvexRadius, jolt_collider.supportBuffer, JPH::Vec3::sReplicate(1.0f));
        }

        if (collider.type == ColliderType::Cylinder){
            auto cylinder = CylinderShape(get_height(collider) / 2, get_radius(collider), JPH::min(get_height(collider) / 2, get_radius(collider)));
            jolt_collider.support = cylinder.GetSupportFunction(JPH::ConvexShape::ESupportMode::ExcludeConvexRadius, jolt_collider.supportBuffer, JPH::Vec3::sReplicate(1.0f));

        }

        if (collider.type == ColliderType::Capsule){
            auto capsule = CapsuleShape(get_height(collider) / 2, get_radius(collider));
            jolt_collider.support = capsule.GetSupportFunction(JPH::ConvexShape::ESupportMode::ExcludeConvexRadius, jolt_collider.supportBuffer, JPH::Vec3::sReplicate(1.0f));
        }

        if (collider.type == ColliderType::Box){
            auto box = BoxShape(JPH::Vec3(get_size_x(collider) / 2, get_size_y(collider) / 2, get_size_z(collider) / 2),
                                          JPH::min(get_size_x(collider) / 2, JPH::min(get_size_y(collider) / 2, get_size_z(collider) / 2)));

            jolt_collider.support = box.GetSupportFunction(JPH::ConvexShape::ESupportMode::ExcludeConvexRadius, jolt_collider.supportBuffer, JPH::Vec3::sReplicate(1.0f));
        }

        if (collider.type == ColliderType::Mesh){

            unsigned int vertex_count = get_vertex_count(collider);
            for (int i = 0; i < vertex_count; i++){
                JPH::Float3 vertex = JPH::Float3(collider.vertecies[i].x, collider.vertecies[i].y, collider.vertecies[i].z);
                jolt_collider.vertexList.push_back(vertex);
            }

            /*
            unsigned int index_count = get_index_count(collider);
            unsigned int triangle_count = index_count / 3;
            JPH::IndexedTriangleList indexedTriangleList;
            for (int i = 0; i < triangle_count; i++){
                indexedTriangleList.emplace_back(collider.indicies[i * 3], collider.indicies[i * 3 + 1], collider.indicies[i * 3 + 2]);
            }

            auto mesh_settings = JPH::MeshShapeSettings(vertexList, indexedTriangleList);
            auto result = JPH::Shape::ShapeResult();
            auto mesh = JPH::MeshShape(mesh_settings, result);
             */

            jolt_collider.polygon_support = new JPH::PolygonConvexSupport<JPH::VertexList>(jolt_collider.vertexList);
            jolt_collider.support = (JPH::ConvexShape::Support*)(jolt_collider.polygon_support);

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

        }
    }

    float get_distance(JoltCase& jolt_case){

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
