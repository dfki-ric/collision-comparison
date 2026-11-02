#pragma once

#include "collider.h"

using compare::Base::Collider;
using compare::Base::ColliderType;
using compare::Base::Case;
using compare::Base::SupportMode;

#include <ccd/ccd.h>
#include <climits>
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
        // vertex with the largest dot product with each direction (cx, cy, cz) in {-1, 0, 1}^3 (index 9 cx + 3 cy + cz
        // after adding 1 to each component): start of the hill climbing, as in MuJoCo
        unsigned int extrema[27] = {};
    };

    struct LibccdCollider {
        Collider collider;
        MeshAdjacency adjacency;
        // support vertex of the previous invocation in the current query, invalid (e.g., UINT_MAX) if there is none
        mutable unsigned int last_support_vertex = UINT_MAX;
    };

    struct LibccdCase {
        ccd_t ccd;
        LibccdCollider collider0;
        LibccdCollider collider1;
    };

    void init();
    void get_cases(Case* base_cases, LibccdCase* libccd_cases, int length, SupportMode support_mode);
    bool get_intersection(LibccdCase& libccd_case);
}