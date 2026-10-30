#include "libccd.h"

#include <iostream>
#include <algorithm>
#include <ccd/quat.h> // for work with quaternions

#include <glm/vec3.hpp> // glm::vec3
#include <glm/vec4.hpp> // glm::vec4
#include <glm/mat4x4.hpp> // glm::mat4
#include <glm/ext/matrix_transform.hpp> // glm::translate, glm::rotate, glm::scale
#include <glm/ext/matrix_clip_space.hpp> // glm::perspective


namespace compare::libccd {

    glm::vec3 transform_point(glm::mat4x4 A2B, glm::vec3 point_in_A){
        return glm::vec3(A2B[0][3], A2B[1][3], A2B[2][3]) + glm::mat3x3(A2B) * point_in_A;
    }

    void sphere_support(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){

        const Collider &collider = ((LibccdCollider *)_collider)->collider;
        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);
        ccdVec3Normalize(&dir);

        float radius = Base::get_radius(collider);
        ccd_vec3_t pos;
        ccdVec3Set(&pos, collider.colliderToOrigen[0][3], collider.colliderToOrigen[1][3], collider.colliderToOrigen[2][3]);

        ccdVec3Scale(&dir, radius);
        ccdVec3Add(&dir, &pos);
        ccdVec3Copy(_vec, &dir);
    }

    void cylider_support(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){

        const Collider &collider = ((LibccdCollider *)_collider)->collider;
        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);

        glm::vec3 local_dir = glm::transpose(glm::mat3x3(collider.colliderToOrigen)) * glm::vec3(dir.v[0], dir.v[1], dir.v[2]);
        float s = glm::sqrt(local_dir[0] * local_dir[0] + local_dir[1] * local_dir[1]);


        float z;
        if (local_dir[2] < 0.0){
            z = -0.5f * Base::get_height(collider);
        } else {
            z = 0.5f * Base::get_height(collider);
        }

        glm::vec3 local_vertex;
        if (s == 0.0) {
            local_vertex[0] = Base::get_radius(collider);
            local_vertex[1] = 0;
            local_vertex[2] = z;
        } else {
            float d = Base::get_radius(collider) / s;
            local_vertex[0] = local_dir[0] * d;
            local_vertex[1] = local_dir[1] * d;
            local_vertex[2] = z;
        }


        glm::vec3 result = transform_point(collider.colliderToOrigen, local_vertex);

        ccdVec3Set(_vec, result[0], result[1], result[2]);
    }

    void capsule_support(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){

        const Collider &collider = ((LibccdCollider *)_collider)->collider;
        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);

        glm::vec3 local_dir = glm::transpose(glm::mat3x3(collider.colliderToOrigen)) * glm::vec3(dir.v[0], dir.v[1], dir.v[2]);
        float s = glm::sqrt(local_dir[0] * local_dir[0] + local_dir[1] * local_dir[1] + local_dir[2] * local_dir[2]);

        glm::vec3 local_vertex;
        if (s == 0.0) {
            local_vertex[0] = Base::get_radius(collider);
            local_vertex[1] = 0;
            local_vertex[2] = 0;
        }
        else {
            local_vertex = local_dir * (Base::get_radius(collider) / s);
        }

        if (local_dir[2] > 0.0){
            local_vertex[2] += 0.5 * Base::get_height(collider);
        }
        else{
            local_vertex[2] -= 0.5 * Base::get_height(collider);
        }

        glm::vec3 result = transform_point(collider.colliderToOrigen, local_vertex);

        ccdVec3Set(_vec, result[0], result[1], result[2]);
    }

    void box_support(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){

        const Collider &collider = ((LibccdCollider *)_collider)->collider;
        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);

        glm::vec3 local_dir = glm::transpose(glm::mat3x3(collider.colliderToOrigen)) * glm::vec3(dir.v[0], dir.v[1], dir.v[2]);

        glm::vec3 local_vertex;
        local_vertex[0] = Base::get_size_x(collider) * (0.5f * (local_dir[0] >= 0) + -0.5f * (local_dir[0] < 0));
        local_vertex[1] = Base::get_size_y(collider) * (0.5f * (local_dir[1] >= 0) + -0.5f * (local_dir[1] < 0));
        local_vertex[2] = Base::get_size_z(collider) * (0.5f * (local_dir[2] >= 0) + -0.5f * (local_dir[2] < 0));

        glm::vec3 result = transform_point(collider.colliderToOrigen, local_vertex);
        ccdVec3Set(_vec, result[0], result[1], result[2]);

    }

    // Support function which checks each vertex in the mesh, works in linear time
    void mesh_support_linear(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){
        const Collider &collider = ((LibccdCollider *)_collider)->collider;

        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);
        const glm::vec3 local_dir = glm::transpose(glm::mat3x3(collider.colliderToOrigen)) * glm::vec3(dir.v[0], dir.v[1], dir.v[2]);

        ccd_real_t score = 0;
        ccd_real_t max_score = 0;
        int best_idx = 0;

        // if for some reason the body does not have any vertices,
        // trying to look up the vertex at index 0 would lead to undefined behavior
        assert(Base::get_vertex_count(collider) >= 1);

        for (int i = 0; i < Base::get_vertex_count(collider); i++){
            score = glm::dot(collider.vertecies[i], local_dir);
            if (score > max_score){
                max_score = score;
                best_idx = i;
            }
        }

        glm::vec3 result = transform_point(collider.colliderToOrigen, collider.vertecies[best_idx]);
        ccdVec3Set(_vec, result[0], result[1], result[2]);
    }


    // support function which implements hill climbing for convex meshes, works in roughly logarithmic time
    void mesh_support(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){
        auto *wrapper = (LibccdCollider *)_collider;
        const Collider &collider = wrapper->collider;
        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);
        const glm::vec3 local_dir = glm::transpose(glm::mat3x3(collider.colliderToOrigen)) * glm::vec3(dir.v[0], dir.v[1], dir.v[2]);

        // if for some reason the body does not have any vertices,
        // trying to look up the vertex at index 0 would lead to undefined behavior
        assert(Base::get_vertex_count(collider) >= 1);

        unsigned int vertex_count = (unsigned int) Base::get_vertex_count(collider);
        // initialize the "current" vertex using the result of the previous invocation, or 0 if the last result is invalid
        unsigned int current = wrapper->last_support_vertex < vertex_count ? wrapper->last_support_vertex : 0;
        float current_score = glm::dot(collider.vertecies[current], local_dir);

        const std::vector<unsigned int> &neighbor_offsets = wrapper->adjacency.neighbor_offsets;
        const std::vector<unsigned int> &neighbors = wrapper->adjacency.neighbors;

        bool improved = true;
        while (improved) {
            improved = false;

            unsigned int begin = neighbor_offsets[current];
            unsigned int end   = neighbor_offsets[current + 1];

            // iterate through all neighbors of the "current" vertex and find the neighbor with the highest dot product
            for (unsigned int i = begin; i < end; i++) {
                unsigned int neighbor = neighbors[i];
                float score = glm::dot(collider.vertecies[neighbor], local_dir);
                if (score > current_score) {
                    current_score = score;
                    current = neighbor;
                    improved = true;
                }
            }
        }

        wrapper->last_support_vertex = current;

        glm::vec3 result = transform_point(collider.colliderToOrigen, collider.vertecies[current]);
        ccdVec3Set(_vec, result[0], result[1], result[2]);
    }

    ccd_support_fn get_support_function(Collider collider, bool force_linear_support_func){
        if (collider.type == ColliderType::Sphere){
            return sphere_support;
        }

        if (collider.type == ColliderType::Cylinder){
            return cylider_support;
        }

        if (collider.type == ColliderType::Capsule){
            return capsule_support;
        }

        if (collider.type == ColliderType::Box){
            return box_support;
        }

        if (collider.type == ColliderType::Mesh){
            if (force_linear_support_func){
                return mesh_support_linear;
            } else {
                return mesh_support;
            }
        }
        std::cerr << "libccd::get_support_function: unknown collider type" << std::endl;
        return nullptr;
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

    void first_dir(const void *_collider0, const void *_collider1, ccd_vec3_t *dir){
        const Collider &collider0 = ((LibccdCollider *)_collider0)->collider;
        const Collider &collider1 = ((LibccdCollider *)_collider1)->collider;

        glm::vec3 origin0(collider0.colliderToOrigen[0][3], collider0.colliderToOrigen[1][3], collider0.colliderToOrigen[2][3]);
        glm::vec3 origin1(collider1.colliderToOrigen[0][3], collider1.colliderToOrigen[1][3], collider1.colliderToOrigen[2][3]);

        glm::vec3 diff = origin1 - origin0;

        // If the origins are too close, use (1,0,0) instead
        if (glm::dot(diff, diff) < 1e-12f){
            ccdVec3Set(dir, 1, 0, 0);
            return;
        }

        ccdVec3Set(dir, diff[0], diff[1], diff[2]);
    }


    void get_case(Collider collider0, Collider collider1, LibccdCase& libccd_case, bool force_linear_support_func){
        CCD_INIT(&libccd_case.ccd);

        libccd_case.collider0.collider = collider0;
        libccd_case.collider1.collider = collider1;
        libccd_case.collider0.last_support_vertex = 0;
        libccd_case.collider1.last_support_vertex = 0;
        build_adjacency(collider0, libccd_case.collider0.adjacency);
        build_adjacency(collider1, libccd_case.collider1.adjacency);

        libccd_case.ccd.support1       = get_support_function(collider0, force_linear_support_func);
        libccd_case.ccd.support2       = get_support_function(collider1, force_linear_support_func);
        libccd_case.ccd.max_iterations = 100;
        libccd_case.ccd.first_dir = first_dir;
    }

    void get_cases(Case *base_cases, LibccdCase *libccd_cases, int length, bool force_linear_support_func){
        for (int i = 0; i < length; i++) {
            get_case(base_cases[i].collider0, base_cases[i].collider1, libccd_cases[i], force_linear_support_func);
        }
    }

    bool get_intersection(LibccdCase& libccd_case) {
        int intersect = ccdGJKIntersect(&libccd_case.collider0, &libccd_case.collider1, &libccd_case.ccd);
        return intersect == 1;
    }
}