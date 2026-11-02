
#pragma once

#include "collider.h"
#include "openGJK_impl.h"
#include <vector>

using compare::Base::Collider;
using compare::Base::ColliderType;
using compare::Base::Case;
using compare::Base::SupportMode;

namespace compare::OpenGJK {
    struct OpenGJKCase {
        OpenGJKCollider collider0;
        OpenGJKCollider collider1;
    };

    void get_cases(const Case* base_cases, OpenGJKCase* openGJK_cases, int length);
    float get_distance(OpenGJKCase& openGJK_case, SupportMode support_mode);
}


