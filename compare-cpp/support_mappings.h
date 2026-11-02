
#ifndef COLLISION_COMPARISON_SUPPORT_MAPPINGS_H
#define COLLISION_COMPARISON_SUPPORT_MAPPINGS_H

#endif //COLLISION_COMPARISON_SUPPORT_MAPPINGS_H
#include "openGJK_impl.h"

void support_sphere(OpenGJKCollider& body, const gkFloat *v);

void support_capsule(OpenGJKCollider& body, const gkFloat *v);

void support_cylinder(OpenGJKCollider& body, const gkFloat *v);

void support_box(OpenGJKCollider& body, const gkFloat *v);

void support_mesh(OpenGJKCollider& body, const gkFloat *v);

void support_mesh_linear(OpenGJKCollider& body, const gkFloat *v);

void support_mesh_extremes(OpenGJKCollider& body, const gkFloat *v);

// largest mesh (number of vertices) that uses plain hill climbing in SupportMode::Adaptive: up to this size, it is
// faster than hill climbing with cached extremes in the support function study on the icosphere benchmarks
// (compare-python/analyze/support_study.py: crossover between 111 and 129 vertices)
constexpr int OPENGJK_HILL_CLIMBING_MAX_VERTICES = 125;
