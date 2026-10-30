#include "openGJK.h"

#include <iostream>


#include "openGJK_impl.h"
#include <algorithm>


#include <math.h>

namespace compare::OpenGJK {
    void get_transform(const Collider& collider, gkBody& gkBody){
        for (int x = 0; x < 3; x++){
            for (int y = 0; y < 3; y++){
                gkBody.rotation_mat[x][y] = collider.colliderToOrigen[x][y];
            }
        }
        gkBody.translation[0] = collider.colliderToOrigen[0][3];
        gkBody.translation[1] = collider.colliderToOrigen[1][3];
        gkBody.translation[2] = collider.colliderToOrigen[2][3];
    }

    void get_collider(const Collider& collider, gkBody& gkBody){
        if (collider.type == ColliderType::Sphere){
            gkBody.type = Sphere;
            gkBody.radius = get_radius(collider);
        }

        if (collider.type == ColliderType::Cylinder){
            gkBody.type = Cylinder;
            gkBody.radius = get_radius(collider);
            gkBody.height = get_height(collider);
        }

        if (collider.type == ColliderType::Capsule){
            gkBody.type = Capsule;
            gkBody.radius = get_radius(collider);
            gkBody.height = get_height(collider);
        }

        if (collider.type == ColliderType::Box){
            gkBody.type = Box;
            gkBody.half_x_length = get_size_x(collider) / 2.0;
            gkBody.half_y_length = get_size_y(collider) / 2.0;
            gkBody.half_z_length = get_size_z(collider) / 2.0;
        }

        if (collider.type == ColliderType::Mesh){
            gkBody.type = Mesh;
            gkBody.numpoints = get_vertex_count(collider);

            gkBody.coord = static_cast<gkFloat**>(malloc(gkBody.numpoints * sizeof(gkFloat*)));
            for (int i = 0; i < gkBody.numpoints; i++) {
                gkBody.coord[i] = static_cast<gkFloat*>(malloc(3 * sizeof(gkFloat)));
            }
            for (int i = 0; i < gkBody.numpoints; i++){
                gkBody.coord[i][0] = collider.vertecies[i].x;
                gkBody.coord[i][1] = collider.vertecies[i].y;
                gkBody.coord[i][2] = collider.vertecies[i].z;
            }
        }
    }

    // Builds the vertex adjacency graph in CSR form for a mesh collider:
    void build_adjacency(const Collider &collider, MeshAdjacency &adjacency){
        if (collider.type != ColliderType::Mesh){
            return;
        }

        int vertex_count = Base::get_vertex_count(collider);
        int index_count = Base::get_index_count(collider);

        std::vector<std::vector<unsigned int>> neighbor_sets(vertex_count);
        auto add_edge = [&neighbor_sets](unsigned int a, unsigned int b) {
            std::vector<unsigned int> &neighbor_list = neighbor_sets[a];
            // if vertex b has not yet been registered as a neighbor of vertex a, add it to a's neighbors
            if (std::find(neighbor_list.begin(), neighbor_list.end(), b) == neighbor_list.end()) {
                neighbor_list.push_back(b);
            }
        };

        // iterate through every triangle in the mesh and add every edge into the adjacency graph
        for (int f = 0; f + 2 < index_count; f += 3) {
            unsigned int a = collider.indicies[f];
            unsigned int b = collider.indicies[f + 1];
            unsigned int c = collider.indicies[f + 2];
            add_edge(a, b); add_edge(b, a);
            add_edge(b, c); add_edge(c, b);
            add_edge(c, a); add_edge(a, c);
        }

        adjacency.neighbor_offsets.resize(vertex_count + 1);
        unsigned int total = 0;
        for (int i = 0; i < vertex_count; i++) {
            adjacency.neighbor_offsets[i] = total;
            total += (unsigned int) neighbor_sets[i].size();
        }
        adjacency.neighbor_offsets[vertex_count] = total;

        adjacency.neighbors.resize(total);
        unsigned int cursor = 0;
        for (int i = 0; i < vertex_count; i++) {
            for (unsigned int neighbor : neighbor_sets[i]) {
                adjacency.neighbors[cursor++] = neighbor;
            }
        }
    }

    void get_case(const Collider& collider0, const Collider& collider1, OpenGJKCase& openGJK_case){
        get_collider(collider0, openGJK_case.collider0.collider);
        get_collider(collider1, openGJK_case.collider1.collider);

        get_transform(collider0, openGJK_case.collider0.collider);
        get_transform(collider1, openGJK_case.collider1.collider);

        openGJK_case.collider0.last_support_vertex = 0;
        openGJK_case.collider1.last_support_vertex = 0;
        build_adjacency(collider0, openGJK_case.collider0.adjacency);
        build_adjacency(collider1, openGJK_case.collider1.adjacency);
    }

    void get_cases(const Case* base_cases, OpenGJKCase* openGJK_cases, int length){

        for (int i = 0; i < length; i++) {

            const auto base_case = base_cases[i];
            get_case(base_case.collider0, base_case.collider1, openGJK_cases[i]);

        }
    }

    float get_distance(const OpenGJKCase& openGJK_case, bool force_linear_support_func) {
        /* Initialize simplex as empty */
        gkSimplex s;
        s.nvrtx = 0;

        /* Compute distance */
        const gkFloat dd = compute_minimum_distance(openGJK_case.collider0, openGJK_case.collider1, &s, force_linear_support_func);

        return static_cast<float>(dd);
    }
}
