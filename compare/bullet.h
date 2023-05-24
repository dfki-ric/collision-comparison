
#pragma once

# include "BulletCollision/CollisionShapes/btSphereShape.h"
# include "BulletCollision/CollisionShapes/btCapsuleShape.h"
# include "BulletCollision/CollisionShapes/btCylinderShape.h"
# include "BulletCollision/CollisionShapes/btBoxShape.h"

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