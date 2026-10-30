#include "openGJK_impl.h"
#include "support_mappings.h"
#include "math.h"

#define dotProduct(a, b) (a[0] * b[0] + a[1] * b[1] + a[2] * b[2])

void transpose3x3(const gkFloat src[3][3], gkFloat dest[3][3]) {
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            dest[j][i] = src[i][j];
        }
    }
}

void rotateVector3D(const gkFloat matrix[3][3], const gkFloat vec[3], gkFloat result[3]) {
    for (int i = 0; i < 3; i++) {
        result[i] = 0.0;
        for (int j = 0; j < 3; j++) {
            result[i] += matrix[i][j] * vec[j];
        }
    }
}

void support_sphere(OpenGJKCollider& body, const gkFloat *v) {
    gkBody& collider = body.collider;
    gkFloat vertex_local[3] = {0, 0, 0};
    const gkFloat v_length = sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    if (v_length == 0.0){
        vertex_local[0] = 0;
        vertex_local[1] = 0;
        vertex_local[2] = collider.radius;
    } else{
        vertex_local[0] = v[0] / v_length * collider.radius;
        vertex_local[1] = v[1] / v_length * collider.radius;
        vertex_local[2] = v[2] / v_length * collider.radius;
    }

    collider.s[0] = collider.translation[0] + vertex_local[0];
    collider.s[1] = collider.translation[1] + vertex_local[1];
    collider.s[2] = collider.translation[2] + vertex_local[2];
}

void support_capsule(OpenGJKCollider& body, const gkFloat *v) {
    gkBody& collider = body.collider;
    gkFloat rotation_T[3][3];
    transpose3x3(collider.rotation_mat, rotation_T);
    gkFloat local_dir[3];
    rotateVector3D(rotation_T, v, local_dir);

    const gkFloat v_length = sqrt(local_dir[0] * local_dir[0] + local_dir[1] * local_dir[1] + local_dir[2] * local_dir[2]);

    gkFloat vertex_local[3] = {0, 0, 0};
    if (v_length== 0.0){
        vertex_local[0] = collider.radius;
    } else{
        vertex_local[0] = local_dir[0] / v_length * collider.radius;
        vertex_local[1] = local_dir[1] / v_length * collider.radius;
        vertex_local[2] = local_dir[2] / v_length * collider.radius;
    }
    if (local_dir[2] > 0.0){
        vertex_local[2] += 0.5 * collider.height;
    } else{
        vertex_local[2] -= 0.5 * collider.height;
    }

    rotateVector3D(collider.rotation_mat, vertex_local, collider.s);
    collider.s[0] += collider.translation[0];
    collider.s[1] += collider.translation[1];
    collider.s[2] += collider.translation[2];
}

void support_cylinder(OpenGJKCollider& body, const gkFloat *v) {
    gkBody& collider = body.collider;
    gkFloat rotation_T[3][3];
    transpose3x3(collider.rotation_mat, rotation_T);
    gkFloat local_dir[3];
    rotateVector3D(rotation_T, v, local_dir);

    gkFloat s = sqrt(local_dir[0] * local_dir[0] + local_dir[1] * local_dir[1]);

    gkFloat vertex_local[3] = {0, 0, 0};
    vertex_local[2] = collider.height * (local_dir[2] < 0 ? -0.5 : 0.5);

    if (s == 0.0){
        vertex_local[0] = collider.radius;
    } else{
        gkFloat d = collider.radius / s;
        vertex_local[0] = local_dir[0] * d;
        vertex_local[1] = local_dir[1] * d;
    }

    rotateVector3D(collider.rotation_mat, vertex_local, collider.s);
    collider.s[0] += collider.translation[0];
    collider.s[1] += collider.translation[1];
    collider.s[2] += collider.translation[2];
}

void support_box(OpenGJKCollider& body, const gkFloat *v) {
    gkBody& collider = body.collider;
    gkFloat rotation_T[3][3];
    transpose3x3(collider.rotation_mat, rotation_T);
    gkFloat local_dir[3];
    rotateVector3D(rotation_T, v, local_dir);

    gkFloat vertex_local[3] = {0, 0, 0};
    vertex_local[0] = local_dir[0] > 0 ? collider.half_x_length : (local_dir[0] < 0 ? -collider.half_x_length : 0);
    vertex_local[1] = local_dir[1] > 0 ? collider.half_y_length : (local_dir[1] < 0 ? -collider.half_y_length : 0);
    vertex_local[2] = local_dir[2] > 0 ? collider.half_z_length : (local_dir[2] < 0 ? -collider.half_z_length : 0);

    rotateVector3D(collider.rotation_mat, vertex_local, collider.s);
    collider.s[0] += collider.translation[0];
    collider.s[1] += collider.translation[1];
    collider.s[2] += collider.translation[2];
}

// Support function which checks each vertex in the mesh, works in linear time
void support_mesh_linear(OpenGJKCollider& body, const gkFloat *v) {
    gkBody& collider = body.collider;
    gkFloat rotation_T[3][3];
    transpose3x3(collider.rotation_mat, rotation_T);
    gkFloat direction_local[3];
    rotateVector3D(rotation_T, v, direction_local);

    gkFloat s;
    gkFloat* vrt;
    int better = 0;
    gkFloat maxs = -DBL_MAX;

    for (int i = 0; i < collider.numpoints; ++i) {
        vrt = collider.coord[i];
        s = dotProduct(vrt, direction_local);
        if (s > maxs) {
            maxs = s;
            better = i;
        }
    }

    rotateVector3D(collider.rotation_mat, collider.coord[better], collider.s);
    collider.s[0] += collider.translation[0];
    collider.s[1] += collider.translation[1];
    collider.s[2] += collider.translation[2];
}

// support function which implements hill climbing for convex meshes, works in roughly logarithmic time
void support_mesh(OpenGJKCollider& body, const gkFloat *v) {
    gkBody& collider = body.collider;
    gkFloat rotation_T[3][3];
    transpose3x3(collider.rotation_mat, rotation_T);
    gkFloat direction_local[3];
    rotateVector3D(rotation_T, v, direction_local);

    const std::vector<unsigned int>& neighbor_offsets = body.adjacency.neighbor_offsets;
    const std::vector<unsigned int>& neighbors = body.adjacency.neighbors;

    unsigned int vertex_count = (unsigned int) collider.numpoints;
    // initialize the "current" vertex using the result of the previous invocation, or 0 if the last result is invalid
    unsigned int current = body.last_support_vertex < vertex_count ? body.last_support_vertex : 0;
    gkFloat current_score = dotProduct(collider.coord[current], direction_local);

    bool improved = true;
    while (improved) {
        improved = false;

        unsigned int begin = neighbor_offsets[current];
        unsigned int end   = neighbor_offsets[current + 1];

        // iterate through all neighbors of the "current" vertex and find the neighbor with the highest dot product
        for (unsigned int i = begin; i < end; i++) {
            unsigned int neighbor = neighbors[i];
            gkFloat score = dotProduct(collider.coord[neighbor], direction_local);
            if (score > current_score) {
                current_score = score;
                current = neighbor;
                improved = true;
            }
        }
    }

    body.last_support_vertex = current;

    rotateVector3D(collider.rotation_mat, collider.coord[current], collider.s);
    collider.s[0] += collider.translation[0];
    collider.s[1] += collider.translation[1];
    collider.s[2] += collider.translation[2];
}