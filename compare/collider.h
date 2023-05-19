//
// Created by stroby on 19.05.23.
//

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

    float get_radius(Collider collider) {
        return collider.data[0];
    }

    float get_height(Collider collider) {
        return collider.data[1];
    }

    float get_size_x(Collider collider) {
        return collider.data[0];
    }

    float get_size_y(Collider collider) {
        return collider.data[1];
    }

    float get_size_z(Collider collider) {
        return collider.data[2];
    }

    void load();
}

