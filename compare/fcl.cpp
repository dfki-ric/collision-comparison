#include "fcl.h"

/*
 *  Software License Agreement (BSD License)
 *
 *  Copyright (c) 2022, INRIA
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of Willow Garage, Inc. nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 */

/** \author Louis Montaut */

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

namespace compare::FCL {
    Transform3f get_transform(Collider collider){
        Transform3f transform;
        Eigen::Matrix3d m;
        m << collider.colliderToOrigen[0],  collider.colliderToOrigen[1], collider.colliderToOrigen[2],
                collider.colliderToOrigen[4],  collider.colliderToOrigen[5],  collider.colliderToOrigen[6],
                collider.colliderToOrigen[8], collider.colliderToOrigen[9],  collider.colliderToOrigen[10];
        transform.setTransform(m, Vec3f(collider.colliderToOrigen[3], collider.colliderToOrigen[7], collider.colliderToOrigen[11]));

        return transform;
    }

    FCLCollider get_collider(Collider collider){
        FCLCollider fcl_collider;

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

        return fcl_collider;
    }


    FCLCase get_fcl_case(Collider collider0, Collider collider1){

        FCLCase fcl_case;
        Transform3f transform0 = get_transform(collider0);
        Transform3f transform1 = get_transform(collider1);

        fcl_case.collider0 = get_collider(collider0);
        fcl_case.collider1 = get_collider(collider1);

        fcl_case.mink_diff.set(fcl_case.collider0.shape, fcl_case.collider1.shape, transform0, transform1);

        return fcl_case;
    }

    float get_fcl_distance(const FCLCase& fcl_case){
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

        std::cout << "gjk iterations:\n" << gjk.getIterations() << "\n";

        std::cout << "gjk dist:\n" << gjk.distance << "\n";

        return  gjk.distance;
    }
}

