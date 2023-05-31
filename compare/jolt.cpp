#include "jolt.h"

#include <iostream>

#include <Jolt/Jolt.h>

#include <Jolt/Core/JobSystemThreadPool.h>
#include <Jolt/Physics/PhysicsSystem.h>
#include <Jolt/Physics/Body/BodyCreationSettings.h>
#include <Jolt/Physics/Body/BodyActivationListener.h>
#include "Jolt/Physics/Collision/CollideShape.h"

using JPH::SubShapeIDCreator;
using JPH::CollideShapeSettings;

using CollideShapeCollector = JPH::CollisionCollector<JPH::CollideShapeResult, JPH::CollisionCollectorTraitsCollideShape>;

class Collector : public CollideShapeCollector {

public:
    bool has_hit = false;

private:
    void			Reset()											{  };

    void			OnBody(const JPH::Body &inBody)						{ /* Collects nothing by default */ };

    void			AddHit(const ResultType &inResult) {
        has_hit = true;
    }

};

class Filter : public JPH::ShapeFilter {

    bool ShouldCollide(const Shape *inShape2, const JPH::SubShapeID &inSubShapeIDOfShape2) const
    {
        return true;
    }

    bool ShouldCollide(const Shape *inShape1, const JPH::SubShapeID &inSubShapeIDOfShape1, const Shape *inShape2, const JPH::SubShapeID &inSubShapeIDOfShape2) const
    {
        return true;
    }
};

namespace compare::Jolt {

    Mat44 get_transform(Collider collider){
        return Mat44(JPH::Vec4(collider.colliderToOrigen[0], collider.colliderToOrigen[4], collider.colliderToOrigen[8], collider.colliderToOrigen[12]),
                     JPH::Vec4(collider.colliderToOrigen[1], collider.colliderToOrigen[5], collider.colliderToOrigen[9], collider.colliderToOrigen[13]),
                     JPH::Vec4(collider.colliderToOrigen[2], collider.colliderToOrigen[6], collider.colliderToOrigen[10], collider.colliderToOrigen[14]),
                     JPH::Vec4(collider.colliderToOrigen[3], collider.colliderToOrigen[7], collider.colliderToOrigen[11], collider.colliderToOrigen[15]));
    }

    void get_collider(Collider collider, JoltCollider* jolt_collider){
        if (collider.type == ColliderType::Sphere){
            jolt_collider->sphere = SphereShape(get_radius(collider));
            jolt_collider->shape = &jolt_collider->sphere;
        }

        if (collider.type == ColliderType::Cylinder){
            jolt_collider->cylinder = CylinderShape(get_height(collider) / 2, get_radius(collider), JPH::min(get_height(collider) / 2, get_radius(collider)));
            jolt_collider->shape = &jolt_collider->cylinder;
        }

        if (collider.type == ColliderType::Capsule){
            jolt_collider->capsule = CapsuleShape(get_height(collider) / 2, get_radius(collider));
            jolt_collider->shape = &jolt_collider->capsule;
        }

        if (collider.type == ColliderType::Box){
            jolt_collider->box = BoxShape(JPH::Vec3(get_size_x(collider) / 2, get_size_y(collider) / 2, get_size_z(collider) / 2),
                                          JPH::min(get_size_x(collider) / 2, JPH::min(get_size_y(collider) / 2, get_size_z(collider) / 2)));
            jolt_collider->shape = &jolt_collider->box;
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

        SubShapeIDCreator sub_shape_id_creator = SubShapeIDCreator();
        CollideShapeSettings collide_settings = CollideShapeSettings();
        Collector collision_collector = Collector();
        Filter filter = Filter();

        JPH::ConvexShape::sCollideConvexVsConvex(
                jolt_case.collider0.shape, jolt_case.collider1.shape,
                JPH::Vec3(1.0, 1.0, 1.0), JPH::Vec3(1.0, 1.0, 1.0),
                jolt_case.transform0, jolt_case.transform1,
                sub_shape_id_creator, sub_shape_id_creator,
                collide_settings,
                collision_collector,
                filter
        );

        return collision_collector.has_hit ? 0.0 : 1.0;
    }

}
