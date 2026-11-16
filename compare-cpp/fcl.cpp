#include "fcl.h"

#include "collider.h"

#include <Eigen/Geometry>

#include <algorithm>
#include <iostream>
#include <limits>
#include <memory>
#include <vector>

using coal::Box;
using coal::Capsule;
using coal::Scalar;
using coal::Convex;
using coal::Cylinder;
using coal::GJKVariant;
using coal::Sphere;
using coal::Transform3s;
using coal::Triangle;
using coal::Vec3s;
using coal::details::GJK;

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
using compare::Base::SupportMode;

namespace compare::FCL {
    Transform3s get_transform(Collider collider){
        Transform3s transform;
        Eigen::Matrix3d m;
        m << collider.colliderToOrigen[0][0],  collider.colliderToOrigen[0][1], collider.colliderToOrigen[0][2],
                collider.colliderToOrigen[1][0],  collider.colliderToOrigen[1][1],  collider.colliderToOrigen[1][2],
                collider.colliderToOrigen[2][0], collider.colliderToOrigen[2][1],  collider.colliderToOrigen[2][2];
        transform.setTransform(m, Vec3s(collider.colliderToOrigen[0][3], collider.colliderToOrigen[1][3], collider.colliderToOrigen[2][3]));

        return transform;
    }

    void get_collider(Collider collider, FCLCollider& fcl_collider, SupportMode support_mode){
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
            auto vertices = std::make_shared<std::vector<Vec3s>>(vertex_count);
            for (unsigned int i = 0; i < vertex_count; i++){
                (*vertices)[i] = Vec3s(collider.vertecies[i].x, collider.vertecies[i].y, collider.vertecies[i].z);
            }

            const unsigned int index_count = get_index_count(collider);
            const unsigned int triangle_count = index_count / 3;
            auto triangles = std::make_shared<std::vector<Triangle>>(triangle_count);
            for (unsigned int i = 0; i < triangle_count; i++){
                (*triangles)[i] = Triangle(collider.indicies[i * 3], collider.indicies[i * 3 + 1],
                                           collider.indicies[i * 3 + 2]);
            }

            // the constructor computes the vertex graph (neighbors) and Coal's support warm starts: the support
            // vertices of 14 directions, from which the hill climbing starts when the search direction turned by
            // more than about 25 degrees since the last support call
            auto convex = new Convex<Triangle>(vertices, vertex_count, triangles, triangle_count);
            if (support_mode == SupportMode::Linear) {
                // without a vertex graph, Coal's support function of a convex searches all vertices (but the
                // MinkowskiDiff selects hill climbing for more than 32 vertices anyway, see linear_support)
                convex->neighbors.reset();
            } else if (support_mode == SupportMode::CachedExtremes) {
                // hill climbing from the extreme vertex of the grid cell of the direction (3x3x3 grid, as in MuJoCo,
                // compare-cpp/patches/coal-cached-extremes.patch) instead of Coal's support warm starts
                convex->support_warm_starts.points.clear();
                convex->support_warm_starts.indices.clear();
                Scalar max_dot[27];
                std::fill(max_dot, max_dot + 27, std::numeric_limits<Scalar>::lowest());
                for (unsigned int i = 0; i < vertex_count; i++) {
                    int k = 0;
                    for (int cx = -1; cx <= 1; cx++) {
                        for (int cy = -1; cy <= 1; cy++) {
                            for (int cz = -1; cz <= 1; cz++, k++) {
                                const Scalar dot = (*vertices)[i].dot(Vec3s(cx, cy, cz));
                                if (dot > max_dot[k]) {
                                    max_dot[k] = dot;
                                    convex->extrema[k] = (int) i;
                                }
                            }
                        }
                    }
                }
                convex->use_extrema = true;
            }
            // SupportMode::HillClimbing: Coal's default (hill climbing with its support warm starts)
            fcl_collider.shape = convex;
        }
    }

    // Support function of the Minkowski difference with Coal's generic support function of each shape, which
    // searches all vertices of a convex without vertex graph. Coal itself selects hill climbing for convexes with more
    // than 32 vertices (and has no option to change that), so the linear search needs this replacement.
    void linear_support(const coal::details::MinkowskiDiff& md, const Vec3s& dir, Vec3s& support0, Vec3s& support1,
                        coal::support_func_guess_t& hint, coal::details::ShapeSupportData /*data*/[2]) {
        support0 = coal::details::getSupport<coal::details::SupportOptions::NoSweptSphere>(md.shapes[0], dir, hint[0]);
        support1 = md.oR1 * coal::details::getSupport<coal::details::SupportOptions::NoSweptSphere>(
                md.shapes[1], -md.oR1.transpose() * dir, hint[1]) + md.ot1;
    }

    void get_case(Collider collider0, Collider collider1, FCLCase& fcl_case, SupportMode support_mode){

        Transform3s transform0 = get_transform(collider0);
        Transform3s transform1 = get_transform(collider1);

        get_collider(collider0, fcl_case.collider0, support_mode);
        get_collider(collider1, fcl_case.collider1, support_mode);

        fcl_case.mink_diff.set(fcl_case.collider0.shape, fcl_case.collider1.shape, transform0, transform1);
        if (support_mode == SupportMode::Linear) {
            fcl_case.mink_diff.getSupportFunc = &linear_support;
        }
    }

    void get_cases(Case* base_cases, FCLCase* fcl_cases, int length, SupportMode support_mode){

        for (int i = 0; i < length; i++) {
            get_case(base_cases[i].collider0, base_cases[i].collider1, fcl_cases[i], support_mode);
        }
    }

    namespace {
        // GJK with the same parameters for all variants: at most 128 iterations, relative tolerance 1e-6 of van den
        // Bergen's convergence criterion (Coal's default), initial guess: origin of collider 1 in the frame of
        // collider 0. normalize: normalized support directions of Nesterov acceleration (Coal sets them only for
        // pairs of convex meshes, here they are set explicitly as in the benchmarks of Montaut et al.)
        GJK::Status run_gjk(FCLCase& fcl_case, GJK& gjk, GJKVariant variant, bool normalize) {
            gjk.gjk_variant = variant;
            fcl_case.mink_diff.normalize_support_direction = normalize;
            const Vec3s init_guess = -fcl_case.mink_diff.ot1;
            return gjk.evaluate(fcl_case.mink_diff, init_guess);
        }

        float distance(FCLCase& fcl_case, GJKVariant variant, bool normalize) {
            GJK gjk(128, 1e-6);
            const GJK::Status status = run_gjk(fcl_case, gjk, variant, normalize);
            if (status == GJK::Status::Failed) {
                std::cerr << "Coal failed to converge while calculating distance" << std::endl;
            }
            return gjk.distance;
        }

        bool intersection(FCLCase& fcl_case, GJKVariant variant, bool normalize) {
            GJK gjk(128, 1e-6);
            gjk.setDistanceEarlyBreak(0);   // if the distance was proven to be more than 0, exit early
            const GJK::Status status = run_gjk(fcl_case, gjk, variant, normalize);
            if (status == GJK::Status::Failed) {
                std::cerr << "Coal failed to converge while calculating intersection" << std::endl;
            }
            return status == GJK::Status::Collision || status == GJK::Status::CollisionWithPenetrationInformation;
        }
    }

    float get_distance_default(FCLCase& fcl_case){
        return distance(fcl_case, GJKVariant::DefaultGJK, false);
    }

    bool get_intersection_default(FCLCase& fcl_case){
        return intersection(fcl_case, GJKVariant::DefaultGJK, false);
    }

    float get_distance_nesterov(FCLCase& fcl_case){
        return distance(fcl_case, GJKVariant::NesterovAcceleration, false);
    }

    bool get_intersection_nesterov(FCLCase& fcl_case){
        return intersection(fcl_case, GJKVariant::NesterovAcceleration, false);
    }

    float get_distance_nesterov_normalized(FCLCase& fcl_case){
        return distance(fcl_case, GJKVariant::NesterovAcceleration, true);
    }

    bool get_intersection_nesterov_normalized(FCLCase& fcl_case){
        return intersection(fcl_case, GJKVariant::NesterovAcceleration, true);
    }

    float get_distance_polyak(FCLCase& fcl_case){
        return distance(fcl_case, GJKVariant::PolyakAcceleration, false);
    }

    bool get_intersection_polyak(FCLCase& fcl_case){
        return intersection(fcl_case, GJKVariant::PolyakAcceleration, false);
    }
}
