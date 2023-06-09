
#pragma once

#include "collider.h"
# include "BulletCollision/CollisionShapes/btSphereShape.h"
# include "BulletCollision/CollisionShapes/btCapsuleShape.h"
# include "BulletCollision/CollisionShapes/btCylinderShape.h"
# include "BulletCollision/CollisionShapes/btBoxShape.h"

using compare::Base::Collider;
using compare::Base::ColliderType;
using compare::Base::Case;

namespace compare::Bullet {
    struct BulletCollider {
        btSphereShape sphere;
        btCapsuleShape capsule;
        btCylinderShape cylinder;
        btBoxShape box;

        btConvexShape* shape;
    };

    struct BulletCase {
        btTransform transform0;
        btTransform transform1;

        BulletCollider collider0;
        BulletCollider collider1;
    };

    void get_case(Collider collider0, Collider collider1, BulletCase* bullet_case);
    void get_cases(Case* base_cases, BulletCase* bullet_cases, int length);
    float get_distance(BulletCase* bullet_case);
}


