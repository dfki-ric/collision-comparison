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
            fcl_collider.shape = new Sphere(get_radius(collider));
        }

        if (collider.type == ColliderType::Cylinder){
            fcl_collider.shape = new Cylinder(get_radius(collider), get_height(collider));
        }

        if (collider.type == ColliderType::Capsule){
            fcl_collider.shape = new Capsule(get_radius(collider), get_height(collider));
        }

        if (collider.type == ColliderType::Box){
            fcl_collider.shape = new Box(get_size_x(collider), get_size_y(collider), get_size_z(collider));
        }

        if (collider.type == ColliderType::Mesh){

            const unsigned int vertex_count = get_vertex_count(collider);
            const auto vertices = new Vec3f[vertex_count];
            for (int i = 0; i < vertex_count; i++){
                vertices[i][0] = collider.vertecies[i].x;
                vertices[i][1] = collider.vertecies[i].y;
                vertices[i][2] = collider.vertecies[i].z;
            }

            const unsigned int index_count = get_index_count(collider);
            const unsigned int triangle_count = index_count / 3;
            const auto triangles = new Triangle[triangle_count];
            for (int i = 0; i < triangle_count; i++){
                triangles[i][0] = collider.indicies[i * 3];
                triangles[i][1] = collider.indicies[i * 3 + 1];
                triangles[i][2] = collider.indicies[i * 3 + 2];
            }

            fcl_collider.shape = new Convex<Triangle>(
                true,
                vertices, vertex_count,
                triangles, triangle_count
                );
        }
    }

    void get_case(Collider collider0, Collider collider1, FCLCase& fcl_case, bool force_linear_support_func){

        Transform3f transform0 = get_transform(collider0);
        Transform3f transform1 = get_transform(collider1);

        get_collider(collider0, fcl_case.collider0);
        get_collider(collider1, fcl_case.collider1);

        if (force_linear_support_func) {
            fcl_case.mink_diff.linear_log_convex_threshold = INT32_MAX;
        }
        fcl_case.mink_diff.set(fcl_case.collider0.shape, fcl_case.collider1.shape, transform0, transform1);
    }

    void get_cases(Case* base_cases, FCLCase* fcl_cases, int length, bool force_linear_support_func){

        for (int i = 0; i < length; i++) {
            get_case(base_cases[i].collider0, base_cases[i].collider1, fcl_cases[i], force_linear_support_func);
        }
    }

    float get_distance_nesterov(FCLCase& fcl_case){
        unsigned int max_iterations = 128;
        FCL_REAL tolerance = 1e-6;
        GJK gjk(max_iterations, tolerance);
        gjk.gjk_variant = GJKVariant::NesterovAcceleration;

        // use origin of collider 1 in the frame of collider 0 as initial support function guess
        Vec3f init_guess = -fcl_case.mink_diff.ot1;
        GJK::Status res_gjk = gjk.evaluate(fcl_case.mink_diff, init_guess);

        if (res_gjk  == GJK::Status::Failed){
            std::cerr << "HPP-FCL failed to converge while calculating distance" << std::endl;
        }
        return  gjk.distance;
    }

    bool get_intersection_nesterov(FCLCase& fcl_case){
        unsigned int max_iterations = 128;
        FCL_REAL tolerance = 1e-6;
        GJK gjk(max_iterations, tolerance);
        gjk.gjk_variant = GJKVariant::NesterovAcceleration;
        gjk.setDistanceEarlyBreak(0);   // if the distance was proven to be more than 0, exit early

        // use origin of collider 1 in the frame of collider 0 as initial support function guess
        Vec3f init_guess = -fcl_case.mink_diff.ot1;
        GJK::Status res_gjk = gjk.evaluate(fcl_case.mink_diff, init_guess);

        if (res_gjk  == GJK::Status::Failed){
            std::cerr << "HPP-FCL failed to converge while calculating intersection" << std::endl;
        }
        return res_gjk == GJK::Status::Inside;
    }

    float get_distance_default(FCLCase& fcl_case){
        unsigned int max_iterations = 128;
        FCL_REAL tolerance = 1e-6;
        GJK gjk(max_iterations, tolerance);
        gjk.gjk_variant = GJKVariant::DefaultGJK;

        // use origin of collider 1 in the frame of collider 0 as initial support function guess
        Vec3f init_guess = -fcl_case.mink_diff.ot1;
        GJK::Status res_gjk = gjk.evaluate(fcl_case.mink_diff, init_guess);

        if (res_gjk  == GJK::Status::Failed){
            std::cerr << "HPP-FCL failed to converge while calculating distance" << std::endl;
        }
        return  gjk.distance;
    }

    bool get_intersection_default(FCLCase& fcl_case){
        unsigned int max_iterations = 128;
        FCL_REAL tolerance = 1e-6;
        GJK gjk(max_iterations, tolerance);
        gjk.gjk_variant = GJKVariant::DefaultGJK;
        gjk.setDistanceEarlyBreak(0);   // if the distance was proven to be more than 0, exit early

        // use origin of collider 1 in the frame of collider 0 as initial support function guess
        Vec3f init_guess = -fcl_case.mink_diff.ot1;
        GJK::Status res_gjk = gjk.evaluate(fcl_case.mink_diff, init_guess);

        if (res_gjk  == GJK::Status::Failed){
            std::cerr << "HPP-FCL failed to converge while calculating intersection" << std::endl;
        }
        return res_gjk == GJK::Status::Inside;
    }
}

