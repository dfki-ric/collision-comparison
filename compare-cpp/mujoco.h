#pragma once

// The native GJK of MuJoCo (mjc_gjk, engine_collision_gjk.c) with MuJoCo's own support functions, not the libccd
// fallback of MuJoCo and not the GPU port MuJoCo Warp.

#include "collider.h"

#include <memory>

#include <mujoco/mujoco.h>
#include <engine/engine_collision_convex.h>

using compare::Base::Case;
using compare::Base::SupportMode;

namespace compare::MuJoCo {
    struct MuJoCoCase {
        // model with the meshes of the case file (nullptr if there are none), the mesh support functions use it
        std::shared_ptr<mjModel> model;

        mjCCDObj obj0;
        mjCCDObj obj1;
    };

    // support_mode: MuJoCo's default is SupportMode::CachedExtremes
    void get_cases(Case* base_cases, MuJoCoCase* mujoco_cases, int length,
                   SupportMode support_mode = SupportMode::CachedExtremes);
    float get_distance(MuJoCoCase& mujoco_case);
    bool get_intersection(MuJoCoCase& mujoco_case);
}
