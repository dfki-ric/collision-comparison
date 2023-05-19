#pragma once

namespace compare::Base {
    enum ColliderType {
        Sphere,
        Capsule,
        Cylinder,
        Box,
    };

    struct Collider {
        ColliderType type;
        float colliderToOrigen[16];
        float data[3];
    };

    struct Case {
        int case_index;
        Collider collider0;
        Collider collider1;

        float distance;
    };

    float get_radius(Collider collider);

    float get_height(Collider collider);

    float get_size_x(Collider collider);

    float get_size_y(Collider collider);

    float get_size_z(Collider collider);

    void load_cases(Case* cases, int length);
}

