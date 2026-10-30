//
// Created by stroby on 19.05.23.
//

#include "collider.h"

#include <iostream>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace compare::Base {

    static void load_mesh_from_obj(const std::string& obj_path, Collider* collider) {
        std::ifstream file(obj_path);
        if (!file.is_open()) {
            std::cerr << "Failed to open OBJ file: " << obj_path << "\n";
            return;
        }

        std::vector<glm::vec3> vertices;
        std::vector<unsigned int> indices;

        try {
            std::string line;
            while (std::getline(file, line)) {
                if (line.rfind("v ", 0) == 0) {
                    std::istringstream ss(line.substr(2));
                    glm::vec3 v;
                    ss >> v.x >> v.y >> v.z;
                    if (ss.fail()) {
                        throw std::runtime_error("Expected 3 floats after 'v', got: '" + line + "'");
                    }
                    vertices.push_back(v);
                } else if (line.rfind("f ", 0) == 0) {
                    std::istringstream ss(line.substr(2));
                    unsigned int a, b, c;
                    ss >> a >> b >> c;
                    if (ss.fail()) {
                        throw std::runtime_error("Expected 3 integer indices after 'f', got: '" + line + "'");
                    }
                    // OBJ indices are 1-based
                    indices.push_back(a - 1);
                    indices.push_back(b - 1);
                    indices.push_back(c - 1);
                }
            }

            if (vertices.empty()) throw std::runtime_error("OBJ file contains no vertices");
            if (indices.empty()) throw std::runtime_error("OBJ file contains no faces");
        } catch (const std::runtime_error& e) {
            throw std::runtime_error(
                "Failed to parse OBJ file '" + obj_path + "': " + e.what()
            );
        }

        int vertices_len = (int) vertices.size();
        collider->vertecies = new glm::vec3[vertices_len];
        collider->data[0] = (float) vertices_len;
        for (int i = 0; i < vertices_len; i++) {
            collider->vertecies[i] = vertices[i];
        }

        int indices_len = (int) indices.size();
        collider->indicies = new unsigned int[indices_len];
        collider->data[1] = (float) indices_len;
        for (int i = 0; i < indices_len; i++) {
            collider->indicies[i] = indices[i];
        }
    }

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

    void parseCollider(json collider_json, Collider* collider, const std::string& data_dir) {

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

            const std::string mesh_path = collider_json["mesh_path"];
            const std::string full_obj_path = data_dir + "/" + mesh_path;
            load_mesh_from_obj(full_obj_path, collider);
        }

        collider->colliderToOrigen[0][0] = collider_json["collider2origin"][0][0];
        collider->colliderToOrigen[0][1] = collider_json["collider2origin"][0][1];
        collider->colliderToOrigen[0][2] = collider_json["collider2origin"][0][2];
        collider->colliderToOrigen[0][3] = collider_json["collider2origin"][0][3];

        collider->colliderToOrigen[1][0] = collider_json["collider2origin"][1][0];
        collider->colliderToOrigen[1][1] = collider_json["collider2origin"][1][1];
        collider->colliderToOrigen[1][2] = collider_json["collider2origin"][1][2];
        collider->colliderToOrigen[1][3] = collider_json["collider2origin"][1][3];

        collider->colliderToOrigen[2][0] = collider_json["collider2origin"][2][0];
        collider->colliderToOrigen[2][1] = collider_json["collider2origin"][2][1];
        collider->colliderToOrigen[2][2] = collider_json["collider2origin"][2][2];
        collider->colliderToOrigen[2][3] = collider_json["collider2origin"][2][3];

        collider->colliderToOrigen[3][0] = collider_json["collider2origin"][3][0];
        collider->colliderToOrigen[3][1] = collider_json["collider2origin"][3][1];
        collider->colliderToOrigen[3][2] = collider_json["collider2origin"][3][2];
        collider->colliderToOrigen[3][3] = collider_json["collider2origin"][3][3];
    }

    int load_cases(const char* path, Case* cases, int length) {

        std::string json_path(path);
        std::string data_dir = json_path.substr(0, json_path.find_last_of("/\\"));

        std::ifstream f(path);
        json data = json::parse(f);

        int i = 0;
        for (auto collide_case: data) {
            auto case_index = collide_case["case"];

            Case* base_case = &cases[i];
            parseCollider(collide_case["collider1"], &base_case->collider0, data_dir);
            parseCollider(collide_case["collider2"], &base_case->collider1, data_dir);

            float distance = collide_case["distance"];

            base_case->case_index = case_index;
            base_case->distance = distance;

            i++;

            if (i >= length) {
                break;
            }
        }

        return i;
    }

}

