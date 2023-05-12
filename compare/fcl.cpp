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

#include <Eigen/Geometry>
#include <hpp/fcl/narrowphase/narrowphase.h>
#include <hpp/fcl/shape/geometric_shapes.h>
#include <hpp/fcl/internal/tools.h>

#include "utility.h"

using hpp::fcl::Box;
using hpp::fcl::Capsule;
using hpp::fcl::Sphere;
using hpp::fcl::Cylinder;
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
using hpp::fcl::details::MinkowskiDiff;
using std::size_t;


void test_nesterov_gjk(const ShapeBase& shape0, const ShapeBase& shape1, Transform3f& transform0, Transform3f& transform1) {
  // Solvers
  unsigned int max_iterations = 128;
  FCL_REAL tolerance = 1e-6;
  GJK gjk(max_iterations, tolerance);
  gjk.gjk_variant = GJKVariant::NesterovAcceleration;

  // Minkowski difference
  MinkowskiDiff mink_diff;

  // Same init for both solvers
  Vec3f init_guess = Vec3f(1, 0, 0);
  support_func_guess_t init_support_guess;
  init_support_guess.setZero();

  mink_diff.set(&shape0, &shape1, transform0, transform1);

  // Evaluate both solvers twice, make sure they give the same solution
  GJK::Status res_gjk_1 =
      gjk.evaluate(mink_diff, init_guess, init_support_guess);
  Vec3f ray_gjk = gjk.ray;
  
  
  // Make sure GJK and Nesterov accelerated GJK find the same distance between
  // the shapes
  // BOOST_CHECK(res_nesterov_gjk_1 == res_gjk_1);
  // BOOST_CHECK_SMALL(fabs(ray_gjk.norm() - ray_nesterov.norm()), 1e-4);

  // Make sure GJK and Nesterov accelerated GJK converges in a reasonable
  // amount of iterations
  // BOOST_CHECK(gjk.getIterations() < max_iterations);
  std::cout << "gjk iterations:\n" << gjk.getIterations() << "\n";

  std::cout << "gjk dist:\n" << gjk.distance << "\n";
}

void fcl_hello_world() {

    
    std::cout << "cylinder vs cylinder\n";

  Cylinder cylinder0 = Cylinder(0.510938, 0.127116);
  Cylinder cylinder1 = Cylinder(0.903175, 0.456057);
  

  Transform3f transform0; 
  Eigen::Matrix3d m0;
  m0 << 0.365685,  0.898448, -0.243034,
        -0.739601,  0.439027,  0.510143,
        0.565035, -0.006803,  0.825039;
  transform0.setTransform(m0, Vec3f(-1.556104, 0.765753, -0.834356));

  Transform3f transform1; 
  Eigen::Matrix3d m1;
  m1 << 0.946613,  0.007576,  0.322282,
        0.285324,  0.44562,  -0.848536,
       -0.150044,  0.89519,   0.419668;
  transform1.setTransform(m1, Vec3f(0.394209, 0.433601, 0.332314));

  test_nesterov_gjk(cylinder0, cylinder1, transform0, transform1);
}