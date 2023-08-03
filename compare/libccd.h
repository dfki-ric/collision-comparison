
#pragma once

#include "collider.h"

using compare::Base::Collider;
using compare::Base::ColliderType;
using compare::Base::Case;

#include <ccd/ccd.h>
#include <ccd/quat.h> // for work with quaternions

namespace compare::libccd {

    struct LibccdCase {
        ccd_t ccd;
        Collider collider0;
        Collider collider1;
    };

    void init();
    void get_cases(Case* base_cases, LibccdCase* libccd_cases, int length);
    bool get_intersection(LibccdCase& libccd_case);
}