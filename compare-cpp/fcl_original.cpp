#include "fcl_original.h"

#include <iostream>
#include <vector>

#include <fcl/geometry/shape/box.h>
#include <fcl/geometry/shape/capsule.h>
#include <fcl/geometry/shape/convex.h>
#include <fcl/geometry/shape/cylinder.h>
#include <fcl/geometry/shape/sphere.h>
#include <fcl/narrowphase/detail/convexity_based_algorithm/gjk.h>

using compare::Base::Collider;
using compare::Base::ColliderType;
using compare::Base::get_radius;
using compare::Base::get_height;
using compare::Base::get_size_x;
using compare::Base::get_size_y;
using compare::Base::get_size_z;
using compare::Base::get_vertex_count;
using compare::Base::get_index_count;

namespace compare::FCLOriginal {
    fcl::Transform3d get_transform(Collider collider){
        fcl::Transform3d transform = fcl::Transform3d::Identity();
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                transform.linear()(i, j) = collider.colliderToOrigen[i][j];
            }
            transform.translation()[i] = collider.colliderToOrigen[i][3];
        }
        return transform;
    }

    std::shared_ptr<fcl::ShapeBased> get_shape(Collider collider){
        // like the data, FCL uses the z axis and the full height for cylinders and capsules
        if (collider.type == ColliderType::Sphere){
            return std::make_shared<fcl::Sphered>(get_radius(collider));
        }
        if (collider.type == ColliderType::Cylinder){
            return std::make_shared<fcl::Cylinderd>(get_radius(collider), get_height(collider));
        }
        if (collider.type == ColliderType::Capsule){
            return std::make_shared<fcl::Capsuled>(get_radius(collider), get_height(collider));
        }
        if (collider.type == ColliderType::Box){
            return std::make_shared<fcl::Boxd>(get_size_x(collider), get_size_y(collider), get_size_z(collider));
        }

        // Mesh: the support function of FCL's GJK searches all vertices (FCL's hill climbing over the vertex
        // neighbors is only used by its libccd solver)
        const int vertex_count = get_vertex_count(collider);
        auto vertices = std::make_shared<std::vector<fcl::Vector3d>>(vertex_count);
        for (int i = 0; i < vertex_count; i++){
            (*vertices)[i] = fcl::Vector3d(collider.vertecies[i].x, collider.vertecies[i].y, collider.vertecies[i].z);
        }
        // faces are stored as (number of vertices, vertex indices...)
        const int triangle_count = get_index_count(collider) / 3;
        auto faces = std::make_shared<std::vector<int>>();
        faces->reserve(4 * triangle_count);
        for (int i = 0; i < triangle_count; i++){
            faces->push_back(3);
            for (int k = 0; k < 3; k++) {
                faces->push_back(static_cast<int>(collider.indicies[i * 3 + k]));
            }
        }
        return std::make_shared<fcl::Convexd>(vertices, triangle_count, faces);
    }

    void get_cases(Case* base_cases, FCLOriginalCase* fcl_cases, int length){
        for (int i = 0; i < length; i++) {
            FCLOriginalCase& fcl_case = fcl_cases[i];
            const fcl::Transform3d transform0 = get_transform(base_cases[i].collider0);
            const fcl::Transform3d transform1 = get_transform(base_cases[i].collider1);
            fcl_case.shape0 = get_shape(base_cases[i].collider0);
            fcl_case.shape1 = get_shape(base_cases[i].collider1);

            // as in FCL's GJKSolver_indep::shapeDistance
            fcl_case.mink_diff.shapes[0] = fcl_case.shape0.get();
            fcl_case.mink_diff.shapes[1] = fcl_case.shape1.get();
            fcl_case.mink_diff.toshape1.noalias() = transform1.linear().transpose() * transform0.linear();
            fcl_case.mink_diff.toshape0 = transform0.inverse(Eigen::Isometry) * transform1;
        }
    }

    float get_distance(FCLOriginalCase& fcl_case){
        // default parameters of FCL's GJKSolver_indep
        unsigned int max_iterations = 128;
        double tolerance = 1e-6;
        fcl::detail::GJK<double> gjk(max_iterations, tolerance);

        // like in the HPP-FCL benchmark: the origin of collider 1 in the frame of collider 0 as initial guess
        // (FCL itself starts with (-1, 0, 0) if no cached guess is enabled)
        fcl::Vector3d init_guess = -fcl_case.mink_diff.toshape0.translation();
        fcl::detail::GJK<double>::Status res_gjk = gjk.evaluate(fcl_case.mink_diff, init_guess);

        if (res_gjk == fcl::detail::GJK<double>::Failed){
            std::cerr << "FCL failed to converge while calculating distance" << std::endl;
        }
        return gjk.distance;
    }
}
