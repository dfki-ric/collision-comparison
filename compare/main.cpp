
#include "collider.h"
#include "jolt.h"
#include "fcl.h"
#include "bullet.h"

#include <iostream>

using compare::Base::load_cases;
using compare::Base::Case;

using compare::FCL::FCLCase;
using compare::FCL::get_fcl_cases;
using compare::FCL::get_fcl_distance;

int main(){

    int cases_length = 100;
    Case base_cases[cases_length];

    load_cases(&base_cases[0], cases_length);

    FCLCase fcl_cases[cases_length];

    get_fcl_cases(&base_cases[0], &fcl_cases[0], cases_length);

    for (int i = 0; i < cases_length; i++) {

        float distance = get_fcl_distance(fcl_cases[i]);

        std::cout << distance;

    }

    std::cout << base_cases;

    // load();

	// jolt_hello_world();

	// fcl_hello_world();

	// bullet_hello_world();

	return 0;
}