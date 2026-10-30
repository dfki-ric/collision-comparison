#pragma once

#include "collider.h"

using compare::Base::Collider;
using compare::Base::ColliderType;
using compare::Base::Case;

#include <ccd/ccd.h>
#include <vector>

namespace compare::libccd {

    // Vertex adjacency graph (edges of the mesh), stored in CSR form. Only
    // populated for ColliderType::Mesh colliders. The neighbors of vertex i
    // are neighbors[neighbor_offsets[i] .. neighbor_offsets[i+1]).
    // Built once per case (see get_case() in libccd.cpp) so mesh_support()
    // can hill-climb the graph instead of linearly scanning every vertex.
    struct MeshAdjacency {
        std::vector<unsigned int> neighbor_offsets;
        std::vector<unsigned int> neighbors;
    };

    struct LibccdCollider {
        Collider collider;
        MeshAdjacency adjacency;
        mutable unsigned int last_support_vertex = 0;
    };

    struct LibccdCase {
        ccd_t ccd;
        LibccdCollider collider0;
        LibccdCollider collider1;
    };

    void init();
    void get_cases(Case* base_cases, LibccdCase* libccd_cases, int length, bool force_linear_support_func);
    bool get_intersection(LibccdCase& libccd_case);
}