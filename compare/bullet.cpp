#include "bullet.h"
#include "collider.h"

#include <iostream>
#include <vector>

#include "SphereSphereCollision.h"
#include "BulletCollision/CollisionShapes/btHeightfieldTerrainShape.h"
#include "BulletCollision/CollisionShapes/btSphereShape.h"
#include "BulletCollision/CollisionShapes/btMultiSphereShape.h"

#include "BulletCollision/NarrowPhaseCollision/btComputeGjkEpaPenetration.h"
#include "BulletCollision/NarrowPhaseCollision/btGjkEpa3.h"
#include "BulletCollision/NarrowPhaseCollision/btMprPenetration.h"


# include <BulletCollision/NarrowPhaseCollision/btGjkPairDetector.h>

using compare::Base::Collider;
using compare::Base::ColliderType;

btTransform get_transform(Collider collider){
    return btTransform(
            btMatrix3x3(
                btVector3(collider.colliderToOrigen[0], collider.colliderToOrigen[1], collider.colliderToOrigen[2]),
                btVector3(collider.colliderToOrigen[5], collider.colliderToOrigen[6], collider.colliderToOrigen[7]),
                btVector3(collider.colliderToOrigen[9], collider.colliderToOrigen[10], collider.colliderToOrigen[11])),
            btVector3(collider.colliderToOrigen[4], collider.colliderToOrigen[8], collider.colliderToOrigen[12]));
}

void get_collider(Collider collider, BulletCollider* jolt_collider){
    if (collider.type == ColliderType::Sphere){
        jolt_collider->sphere = btSphereShape(get_radius(collider));
        jolt_collider->shape = &jolt_collider->sphere;
    }

    if (collider.type == ColliderType::Cylinder){
        jolt_collider->cylinder = btCylinderShape(get_height(collider) / 2, get_radius(collider));
        jolt_collider->shape = &jolt_collider->cylinder;
    }

    if (collider.type == ColliderType::Capsule){
        jolt_collider->capsule = btCapsuleShape(get_radius(collider), get_height(collider));
        jolt_collider->shape = &jolt_collider->capsule;
    }

    if (collider.type == ColliderType::Box){
        jolt_collider->box = btBoxShape(btVector3(get_size_x(collider) / 2, get_size_y(collider) / 2, get_size_z(collider) / 2));
        jolt_collider->shape = &jolt_collider->box;
    }
}

