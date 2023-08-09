#include "fcl.h"

#include "collider.h"

#include <Eigen/Geometry>
#include <hpp/fcl/shape/geometric_shapes.h>
#include <hpp/fcl/narrowphase/narrowphase.h>

#include <hpp/fcl/internal/tools.h>

#include "utility.h"

using hpp::fcl::Box;
using hpp::fcl::Capsule;
using hpp::fcl::Sphere;
using hpp::fcl::Cylinder;
using hpp::fcl::Transform3f;
using hpp::fcl::ShapeBase;
using hpp::fcl::details::MinkowskiDiff;

using hpp::fcl::constructPolytopeFromEllipsoid;
using hpp::fcl::Convex;
using hpp::fcl::Ellipsoid;
using hpp::fcl::FCL_REAL;
using hpp::fcl::GJKSolver;
using hpp::fcl::GJKVariant;
using hpp::fcl::ShapeBase;
using hpp::fcl::support_func_guess_t;
using hpp::fcl::Transform3f;
using hpp::fcl::Triangle;
using hpp::fcl::Vec3f;
using hpp::fcl::details::GJK;

using std::size_t;

using compare::Base::Collider;
using compare::Base::ColliderType;
using compare::Base::get_radius;
using compare::Base::get_height;
using compare::Base::get_size_x;
using compare::Base::get_size_y;
using compare::Base::get_size_z;
using compare::Base::get_vertex_count;
using compare::Base::get_index_count;
using compare::Base::Case;

namespace compare::FCL {
    Transform3f get_transform(Collider collider){
        Transform3f transform;
        Eigen::Matrix3d m;
        m << collider.colliderToOrigen[0][0],  collider.colliderToOrigen[0][1], collider.colliderToOrigen[0][2],
                collider.colliderToOrigen[1][0],  collider.colliderToOrigen[1][1],  collider.colliderToOrigen[1][2],
                collider.colliderToOrigen[2][0], collider.colliderToOrigen[2][1],  collider.colliderToOrigen[2][2];
        transform.setTransform(m, Vec3f(collider.colliderToOrigen[0][3], collider.colliderToOrigen[1][3], collider.colliderToOrigen[2][3]));

        return transform;
    }

    void get_collider(Collider collider, FCLCollider& fcl_collider){
        if (collider.type == ColliderType::Sphere){
            fcl_collider.sphere = Sphere(get_radius(collider));
            fcl_collider.shape = &fcl_collider.sphere;
        }

        if (collider.type == ColliderType::Cylinder){
            fcl_collider.cylinder = Cylinder(get_radius(collider), get_height(collider));
            fcl_collider.shape = &fcl_collider.cylinder;
        }

        if (collider.type == ColliderType::Capsule){
            fcl_collider.capsule = Capsule(get_radius(collider), get_height(collider));
            fcl_collider.shape = &fcl_collider.capsule;
        }

        if (collider.type == ColliderType::Box){
            fcl_collider.box = Box(get_size_x(collider), get_size_y(collider), get_size_z(collider));
            fcl_collider.shape = &fcl_collider.box;
        }

        if (collider.type == ColliderType::Mesh){

            unsigned int vertex_count = get_vertex_count(collider);
            fcl_collider.vertecies = new Vec3f[vertex_count];
            for (int i = 0; i < vertex_count; i++){
                fcl_collider.vertecies[i][0] = collider.vertecies[i].x;
                fcl_collider.vertecies[i][1] = collider.vertecies[i].y;
                fcl_collider.vertecies[i][2] = collider.vertecies[i].z;
            }

            unsigned int index_count = get_index_count(collider);
            unsigned int triangle_count = index_count / 3;
            fcl_collider.triangles = new Triangle[triangle_count];
            for (int i = 0; i < triangle_count; i++){
                fcl_collider.triangles[i][0] = collider.indicies[i * 3];
                fcl_collider.triangles[i][1] = collider.indicies[i * 3 + 1];
                fcl_collider.triangles[i][2] = collider.indicies[i * 3 + 2];
            }

            fcl_collider.convex = Convex<Triangle>(true, fcl_collider.vertecies, vertex_count, fcl_collider.triangles, triangle_count);
            fcl_collider.shape = &fcl_collider.convex;
        }
    }

    void get_case(Collider collider0, Collider collider1, FCLCase& fcl_case){

        Transform3f transform0 = get_transform(collider0);
        Transform3f transform1 = get_transform(collider1);

        get_collider(collider0, fcl_case.collider0);
        get_collider(collider1, fcl_case.collider1);

        fcl_case.mink_diff.set(fcl_case.collider0.shape, fcl_case.collider1.shape, transform0, transform1);
    }

    void get_cases(Case* base_cases, FCLCase* fcl_cases, int length){

        for (int i = 0; i < length; i++) {
            get_case(base_cases[i].collider0, base_cases[i].collider1, fcl_cases[i]);
        }
    }

    float get_distance(FCLCase& fcl_case){
        unsigned int max_iterations = 128;
        FCL_REAL tolerance = 1e-6;
        GJK gjk(max_iterations, tolerance);
        gjk.gjk_variant = GJKVariant::NesterovAcceleration;

        // Same init for both solvers
        Vec3f init_guess = Vec3f(1, 0, 0);
        support_func_guess_t init_support_guess;
        init_support_guess.setZero();

        // Evaluate both solvers twice, make sure they give the same solution
        GJK::Status res_gjk = gjk.evaluate(fcl_case.mink_diff, init_guess, init_support_guess);

        // std::cout << "gjk iterations:\n" << gjk.getIterations() << "\n";

        // std::cout << "gjk dist:\n" << gjk.distance << "\n";

        return  gjk.distance;
    }
}

