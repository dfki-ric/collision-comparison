
#include "jolt.h"
#include "fcl.h"
#include "bullet.h"

#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp>
using json = nlohmann::json;


enum ColliderType {
	Sphere,
	Capsule,
	Cylinder,
	Box,
};

struct Collider {
	ColliderType type;
	float colliderToOrigen[16];
	float data[3];
};

float getRadius(Collider collider){
	return collider.data[0];
}

float getHeight(Collider collider){
	return collider.data[1];
}

float getSizeX(Collider collider){
	return collider.data[0];
}

float getSizeY(Collider collider){
	return collider.data[1];
}

float getSizeZ(Collider collider){
	return collider.data[2];
}

Collider parseCollider(json collider_json){

	Collider collider;

	auto type = collider_json["typ"];
	if (type == "Sphere"){
		collider.type = ColliderType::Sphere;	
		collider.data[0] = collider_json["radius"];
	}

	if (type == "Capsule"){
		collider.type = ColliderType::Capsule;	
		collider.data[0] = collider_json["radius"];
		collider.data[1] = collider_json["height"];
	}

	if (type == "Cylinder"){
		collider.type = ColliderType::Cylinder;
		collider.data[0] = collider_json["radius"];
		collider.data[1] = collider_json["height"];
	}

	if (type == "Box"){
		collider.type = ColliderType::Box;
        collider.data[0] = collider_json["size"][0];
        collider.data[1] = collider_json["size"][1];
        collider.data[2] = collider_json["size"][2];
	}

    collider.colliderToOrigen[0] = collider_json["collider2origin"][0][0];
    collider.colliderToOrigen[1] = collider_json["collider2origin"][0][1];
    collider.colliderToOrigen[2] = collider_json["collider2origin"][0][2];
    collider.colliderToOrigen[3] = collider_json["collider2origin"][0][3];

    collider.colliderToOrigen[4] = collider_json["collider2origin"][1][0];
    collider.colliderToOrigen[5] = collider_json["collider2origin"][1][1];
    collider.colliderToOrigen[6] = collider_json["collider2origin"][1][2];
    collider.colliderToOrigen[7] = collider_json["collider2origin"][1][3];

    collider.colliderToOrigen[8] = collider_json["collider2origin"][2][0];
    collider.colliderToOrigen[9] = collider_json["collider2origin"][2][1];
    collider.colliderToOrigen[10] = collider_json["collider2origin"][2][2];
    collider.colliderToOrigen[11] = collider_json["collider2origin"][2][3];

    collider.colliderToOrigen[12] = collider_json["collider2origin"][3][0];
    collider.colliderToOrigen[13] = collider_json["collider2origin"][3][1];
    collider.colliderToOrigen[14] = collider_json["collider2origin"][3][2];
    collider.colliderToOrigen[15] = collider_json["collider2origin"][3][3];


	return collider;
}


void load() {

	std::ifstream f("../../data/test_data.json");
	json data = json::parse(f);

	for (auto collide_case : data)
	{
		auto case_index = collide_case["case"];

		auto collider0 = parseCollider(collide_case["collider1"]);
		auto collider1 = parseCollider(collide_case["collider2"]);

		auto distance = collide_case["distance"];

		std::cout << collider0.type << "\n";
		std::cout << collider1.type << "\n";


		// "it" is of type json::reference and has no key() member
		
	}


}


int main(){

    load();

	// jolt_hello_world();

	// fcl_hello_world();

	// bullet_hello_world();

	return 0;
}