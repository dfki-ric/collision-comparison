
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
