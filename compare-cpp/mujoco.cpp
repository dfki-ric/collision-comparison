#include "mujoco.h"

#include <iostream>
#include <string>
#include <vector>

#include <engine/engine_collision_gjk.h>

using compare::Base::Collider;
using compare::Base::ColliderType;
using compare::Base::get_radius;
using compare::Base::get_height;
using compare::Base::get_size_x;
using compare::Base::get_size_y;
using compare::Base::get_size_z;
using compare::Base::get_vertex_count;
using compare::Base::get_index_count;

namespace compare::MuJoCo {
    // default parameters of MuJoCo (mjOption: ccd_tolerance, ccd_iterations)
    const mjtNum tolerance = 1e-6;
    const int max_iterations = 35;

    void add_geom(mjSpec* spec, const Collider& collider, int geom_index, SupportMode support_mode){
        mjsGeom* geom = mjs_addGeom(mjs_findBody(spec, "world"), nullptr);
        if (support_mode == SupportMode::Linear) {
            // MuJoCo builds the vertex graph of the convex hull only for meshes that can collide; without the graph,
            // mjc_initCCDObj selects the support function that searches all vertices
            geom->contype = 0;
            geom->conaffinity = 0;
        }
        // like the data, MuJoCo uses the z axis for cylinders and capsules, but half sizes
        if (collider.type == ColliderType::Sphere) {
            geom->type = mjGEOM_SPHERE;
            geom->size[0] = get_radius(collider);
        } else if (collider.type == ColliderType::Cylinder) {
            geom->type = mjGEOM_CYLINDER;
            geom->size[0] = get_radius(collider);
            geom->size[1] = 0.5 * get_height(collider);
        } else if (collider.type == ColliderType::Capsule) {
            geom->type = mjGEOM_CAPSULE;
            geom->size[0] = get_radius(collider);
            geom->size[1] = 0.5 * get_height(collider);
        } else if (collider.type == ColliderType::Box) {
            geom->type = mjGEOM_BOX;
            geom->size[0] = 0.5 * get_size_x(collider);
            geom->size[1] = 0.5 * get_size_y(collider);
            geom->size[2] = 0.5 * get_size_z(collider);
        } else {
            const std::string name = "mesh" + std::to_string(geom_index);
            mjsMesh* mesh = mjs_addMesh(spec, nullptr);
            mjs_setName(mesh->element, name.c_str());
            mjs_setFloat(mesh->uservert, &collider.vertecies[0].x, 3 * get_vertex_count(collider));
            std::vector<int> faces(collider.indicies, collider.indicies + get_index_count(collider));
            mjs_setInt(mesh->userface, faces.data(), static_cast<int>(faces.size()));
            geom->type = mjGEOM_MESH;
            mjs_setString(geom->meshname, name.c_str());
        }
    }

    // Model with one geom per collider of the case file (geoms 2i and 2i + 1 for case i): the support functions of
    // MuJoCo are selected by the geom type and use the sizes and meshes of the model. MuJoCo stores the vertices of
    // a mesh in its inertial frame (mesh_pos, mesh_quat) and builds the vertex graph of its convex hull for the hill
    // climbing.
    std::shared_ptr<mjModel> get_model(Case* base_cases, int length, SupportMode support_mode){
        mjSpec* spec = mj_makeSpec();
        for (int i = 0; i < length; i++) {
            add_geom(spec, base_cases[i].collider0, 2 * i, support_mode);
            add_geom(spec, base_cases[i].collider1, 2 * i + 1, support_mode);
        }
        mjModel* model = mj_compile(spec, nullptr);
        if (model == nullptr) {
            std::cerr << "MuJoCo failed to compile the colliders: " << mjs_getError(spec) << std::endl;
            exit(1);
        }
        mj_deleteSpec(spec);
        return std::shared_ptr<mjModel>(model, mj_deleteModel);
    }

    // 27 times the first vertex of the graph: hill climbing without the cached extremes
    const int no_extrema[27] = {};

    void init_obj(mjCCDObj& obj, const Collider& collider, const mjModel* model, int g, SupportMode support_mode){
        mjc_initCCDObj(&obj, model, nullptr, g, 0);
        if (support_mode == SupportMode::HillClimbing && obj.geom_type == mjGEOM_MESH
            && obj.data.mesh.extrema != nullptr) {
            obj.data.mesh.extrema = no_extrema;
        }

        mjtNum pos[3];
        mjtNum mat[9];
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                mat[3 * i + j] = collider.colliderToOrigen[i][j];
            }
            pos[i] = collider.colliderToOrigen[i][3];
        }

        if (collider.type == ColliderType::Mesh) {
            // pose of the mesh frame of MuJoCo, as in mjc_initCCDObjSite
            const int mesh = model->geom_dataid[g];
            mjtNum mesh_mat[9];
            mju_quat2Mat(mesh_mat, model->mesh_quat + 4 * mesh);
            mju_mulMatMat(obj.mat, mat, mesh_mat, 3, 3, 3);
            mju_mulMatVec3(obj.pos, mat, model->mesh_pos + 3 * mesh);
            mju_addTo3(obj.pos, pos);
        } else {
            mju_copy(obj.mat, mat, 9);
            mju_copy3(obj.pos, pos);
        }
    }

    void get_cases(Case* base_cases, MuJoCoCase* mujoco_cases, int length, SupportMode support_mode){
        std::shared_ptr<mjModel> model = get_model(base_cases, length, support_mode);
        for (int i = 0; i < length; i++) {
            mujoco_cases[i].model = model;
            init_obj(mujoco_cases[i].obj0, base_cases[i].collider0, model.get(), 2 * i, support_mode);
            init_obj(mujoco_cases[i].obj1, base_cases[i].collider1, model.get(), 2 * i + 1, support_mode);
        }
    }

    mjtNum run_gjk(MuJoCoCase& mujoco_case, mjtNum dist_cutoff){
        // no warm start from the previous query: the mesh support functions start the hill climbing at the cached
        // vertex (meshindex) if there is one
        mujoco_case.obj0.vertindex = -1;
        mujoco_case.obj0.meshindex = -1;
        mujoco_case.obj1.vertindex = -1;
        mujoco_case.obj1.meshindex = -1;

        // the centers of the colliders as initial guess, as in mjc_ccd
        mjtNum x0[3];
        mjtNum x1[3];
        mju_copy3(x0, mujoco_case.obj0.pos);
        mju_copy3(x1, mujoco_case.obj1.pos);
        return mjc_gjk(&mujoco_case.obj0, &mujoco_case.obj1, x0, x1, dist_cutoff, tolerance, max_iterations);
    }

    float get_distance(MuJoCoCase& mujoco_case){
        // without cutoff, the distance is computed (0 if the colliders intersect)
        return run_gjk(mujoco_case, mjMAX_LIMIT);
    }

    bool get_intersection(MuJoCoCase& mujoco_case){
        // cutoff 0: GJK stops as soon as a separating axis is found (distance mjMAX_LIMIT) or the simplex contains
        // the origin (distance 0, intersection test of MuJoCo after a tetrahedron is found)
        return run_gjk(mujoco_case, 0) < tolerance;
    }
}
