//
// Created by stroby on 19.05.23.
//

#include "collider.h"

#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace compare::Base {

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

    int get_vertex_count(Collider collider){
        return (int) collider.data[0];
    }

    int get_index_count(Collider collider){
        return (int) collider.data[1];
    }

    float get_distance(Case* base_case) {
        return base_case->distance;
    }

    void parseCollider(json collider_json, Collider* collider) {

        auto type = collider_json["type"];
        if (type == "Sphere") {
            collider->type = ColliderType::Sphere;
            collider->data[0] = collider_json["radius"];
        }

        if (type == "Capsule") {
            collider->type = ColliderType::Capsule;
            collider->data[0] = collider_json["radius"];
            collider->data[1] = collider_json["height"];
        }

        if (type == "Cylinder") {
            collider->type = ColliderType::Cylinder;
            collider->data[0] = collider_json["radius"];
            collider->data[1] = collider_json["height"];
        }

        if (type == "Box") {
            collider->type = ColliderType::Box;
            collider->data[0] = collider_json["size"][0];
            collider->data[1] = collider_json["size"][1];
            collider->data[2] = collider_json["size"][2];
        }

        if (type == "Mesh") {
            collider->type = ColliderType::Mesh;

            int vertices_len = collider_json["vertices_len"];
            collider->vertecies = new Vertex[vertices_len];
            collider->data[0] = (float) vertices_len;

            for (int i = 0; i < vertices_len; i++){
                collider->vertecies[i].x = collider_json["vertices"][i][0];
                collider->vertecies[i].y = collider_json["vertices"][i][1];
                collider->vertecies[i].z = collider_json["vertices"][i][2];
            }

            int triangles_len = collider_json["triangles_len"];
            collider->indicies = new unsigned int [triangles_len * 3];
            collider->data[1] = (float) (triangles_len * 3);

            for (int i = 0; i < triangles_len; i++){
                collider->indicies[i * 3] = collider_json["triangles"][i][0];
                collider->indicies[i * 3 + 1] = collider_json["triangles"][i][1];
                collider->indicies[i * 3 + 2] = collider_json["triangles"][i][2];
            }
        }

        collider->colliderToOrigen[0] = collider_json["collider2origin"][0][0];
        collider->colliderToOrigen[1] = collider_json["collider2origin"][0][1];
        collider->colliderToOrigen[2] = collider_json["collider2origin"][0][2];
        collider->colliderToOrigen[3] = collider_json["collider2origin"][0][3];

        collider->colliderToOrigen[4] = collider_json["collider2origin"][1][0];
        collider->colliderToOrigen[5] = collider_json["collider2origin"][1][1];
        collider->colliderToOrigen[6] = collider_json["collider2origin"][1][2];
        collider->colliderToOrigen[7] = collider_json["collider2origin"][1][3];

        collider->colliderToOrigen[8] = collider_json["collider2origin"][2][0];
        collider->colliderToOrigen[9] = collider_json["collider2origin"][2][1];
        collider->colliderToOrigen[10] = collider_json["collider2origin"][2][2];
        collider->colliderToOrigen[11] = collider_json["collider2origin"][2][3];

        collider->colliderToOrigen[12] = collider_json["collider2origin"][3][0];
        collider->colliderToOrigen[13] = collider_json["collider2origin"][3][1];
        collider->colliderToOrigen[14] = collider_json["collider2origin"][3][2];
        collider->colliderToOrigen[15] = collider_json["collider2origin"][3][3];
    }


    void load_cases(Case* cases, int length) {

        std::ifstream f("../../data/test_data.json");
        json data = json::parse(f);

        int i = 0;
        for (auto collide_case: data) {
            auto case_index = collide_case["case"];

            Case* base_case = &cases[i];
            parseCollider(collide_case["collider1"], &base_case->collider0);
            parseCollider(collide_case["collider2"], &base_case->collider1);

            float distance = collide_case["distance"];

            base_case->case_index = case_index;
            base_case->distance = distance;

            i++;

            if (i >= length) {
                break;
            }
        }
    }

}

