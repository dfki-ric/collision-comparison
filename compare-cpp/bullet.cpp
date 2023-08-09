#include "bullet.h"

#include <iostream>

#include "BulletCollision/NarrowPhaseCollision/btComputeGjkEpaPenetration.h"
#include "BulletCollision/NarrowPhaseCollision/btConvexPenetrationDepthSolver.h"
#include "BulletCollision/NarrowPhaseCollision/btMinkowskiPenetrationDepthSolver.h"
#include "BulletCollision/NarrowPhaseCollision/btPointCollector.h"
#include "BulletCollision/NarrowPhaseCollision/btGjkPairDetector.h"
#include "LinearMath/btIDebugDraw.h"


namespace compare::Bullet {
    btTransform get_transform(Collider collider){
        return btTransform(
                btMatrix3x3(
                        btVector3(collider.colliderToOrigen[0][1], collider.colliderToOrigen[1][0], collider.colliderToOrigen[2][0]),
                        btVector3(collider.colliderToOrigen[0][2], collider.colliderToOrigen[1][1], collider.colliderToOrigen[2][1]),
                        btVector3(collider.colliderToOrigen[0][2], collider.colliderToOrigen[1][2], collider.colliderToOrigen[2][2])),
                btVector3(collider.colliderToOrigen[0][3], collider.colliderToOrigen[1][3], collider.colliderToOrigen[2][3]));
    }

    void get_collider(Collider collider, BulletCollider& bullet_collider){
        if (collider.type == ColliderType::Sphere){
            bullet_collider.sphere = btSphereShape(get_radius(collider));
            bullet_collider.shape = &bullet_collider.sphere;
        }

        if (collider.type == ColliderType::Cylinder){
            bullet_collider.cylinder = btCylinderShapeX(btVector3(get_radius(collider), 0.0 , get_height(collider) / 2));
            bullet_collider.shape = &bullet_collider.cylinder;
        }

        if (collider.type == ColliderType::Capsule){
            bullet_collider.capsule = btCapsuleShapeX(get_radius(collider), get_height(collider));
            bullet_collider.shape = &bullet_collider.capsule;
        }

        if (collider.type == ColliderType::Box){
            bullet_collider.box = btBoxShape(btVector3(get_size_x(collider) / 2, get_size_y(collider) / 2, get_size_z(collider) / 2));
            bullet_collider.shape = &bullet_collider.box;
        }
    }

    void get_case(Collider collider0, Collider collider1, BulletCase& bullet_case){
        bullet_case.transform0 = get_transform(collider0);
        bullet_case.transform1 = get_transform(collider1);

        get_collider(collider0, bullet_case.collider0);
        get_collider(collider1, bullet_case.collider1);
    }

    void get_cases(Case* base_cases, BulletCase* bullet_cases, int length){

        for (int i = 0; i < length; i++) {

            auto base_case = base_cases[i];
            get_case(base_case.collider0, base_case.collider1, bullet_cases[i]);

        }
    }

    class Draw : public btIDebugDraw {
        DefaultColors getDefaultColors() const
        {
            DefaultColors colors;
            return colors;
        }

        void drawLine(const btVector3& from, const btVector3& to, const btVector3& color) {}

        void drawContactPoint(const btVector3& PointOnB, const btVector3& normalOnB, btScalar distance, int lifeTime, const btVector3& color) {}

        void reportErrorWarning(const char* warningString) {}

        void draw3dText(const btVector3& location, const char* textString) {}

        void setDebugMode(int debugMode) {}

        int getDebugMode() const { return 0; }

    };

    float get_distance(BulletCase& bullet_case) {
        btVoronoiSimplexSolver voronoiSimplexSolver = btVoronoiSimplexSolver();
        btMinkowskiPenetrationDepthSolver convexPenetrationDepthSolver = btMinkowskiPenetrationDepthSolver();

        btDiscreteCollisionDetectorInterface::ClosestPointInput input;
        input.m_transformA = bullet_case.transform0;
        input.m_transformB = bullet_case.transform1;
        input.m_maximumDistanceSquared = 1000.0;

        btPointCollector result;

        Draw draw = Draw();

        btGjkPairDetector pairDetector = btGjkPairDetector(bullet_case.collider0.shape, bullet_case.collider1.shape, &voronoiSimplexSolver, &convexPenetrationDepthSolver);
        pairDetector.getClosestPointsNonVirtual(input, result, &draw);

        return result.m_distance;
    }
}
