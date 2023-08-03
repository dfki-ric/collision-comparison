#pragma once

#include <glm/vec3.hpp> // glm::vec3
#include <glm/mat4x4.hpp> // glm::mat4

namespace compare::Base {
    enum ColliderType {
        Sphere,
        Capsule,
        Cylinder,
        Box,
        Mesh
    };

    struct Collider {
        ColliderType type;
        glm::mat4x4 colliderToOrigen;
        glm::vec3 data;
        glm::vec3* vertecies;
        unsigned int* indicies;
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

    int get_vertex_count(Collider collider);

    int get_index_count(Collider collider);

    float get_distance(Case* base_case);

    void load_cases(char* path, Case* cases, int length);
}

