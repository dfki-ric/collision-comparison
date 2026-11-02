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

    // Support function for meshes (primitive shapes always use their own support functions):
    // - Linear: searches all vertices
    // - HillClimbing: hill climbing over the vertex graph of the mesh
    // - CachedExtremes: hill climbing that starts at the vertex that is extreme in the direction of a 3x3x3 grid cell
    //   (computed once per mesh), as in MuJoCo
    // - Adaptive: HillClimbing for meshes with at most a library-specific number of vertices, CachedExtremes for
    //   larger meshes (threshold from the support function study, see compare-python/analyze/support_study.py; the
    //   linear search is never faster than HillClimbing there)
    enum class SupportMode {
        Linear,
        HillClimbing,
        CachedExtremes,
        Adaptive
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

    int load_cases(const char* path, Case* cases, int length);
}

