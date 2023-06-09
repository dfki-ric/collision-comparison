
#include "collider.h"
#include "jolt.h"
#include "fcl.h"
#include "bullet.h"

#include <iostream>

#define ANKERL_NANOBENCH_IMPLEMENT
#include <nanobench.h>

using compare::Base::load_cases;
using compare::Base::Case;

using compare::FCL::FCLCase;
using compare::Jolt::JoltCase;
using compare::Bullet::BulletCase;

int main(){

    int cases_length = 100;

    Case base_cases[cases_length];
    load_cases(&base_cases[0], cases_length);

    FCLCase fcl_cases[cases_length];
    compare::FCL::get_cases(&base_cases[0], &fcl_cases[0], cases_length);

    JoltCase jolt_cases[cases_length];
    compare::Jolt::get_cases(&base_cases[0], &jolt_cases[0], cases_length);

    BulletCase bullet_cases[cases_length];
    compare::Bullet::get_cases(&base_cases[0], &bullet_cases[0], cases_length);

#ifdef NDEBUG
    std::cout << "\n\n";

    ankerl::nanobench::Bench().minEpochIterations(1000).run("FCL", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_distance(fcl_cases[i]);
        }
    });

    ankerl::nanobench::Bench().minEpochIterations(1000).run("Jolt", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::Jolt::get_distance(jolt_cases[i]);
        }
    });

    ankerl::nanobench::Bench().minEpochIterations(1000).run("Bullet", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::Bullet::get_distance(bullet_cases[i]);
        }
    });


	return 0;
#endif

    for (int i = 0; i < cases_length; i++) {

        float fcl_distance = compare::FCL::get_distance(&fcl_cases[i]);
        float jolt_distance = compare::Jolt::get_distance(&jolt_cases[i]);
        float bullet_distance = compare::Bullet::get_distance(&bullet_cases[i]);

        bool fcl_correct = abs(compare::Base::get_distance(&base_cases[i]) - fcl_distance) < 0.1;
        bool jolt_correct = abs(compare::Base::get_distance(&base_cases[i]) - jolt_distance) < 0.1;
        bool bullet_correct = abs(compare::Base::get_distance(&base_cases[i]) - bullet_distance) < 0.1;

        if (!fcl_correct || !jolt_correct || !bullet_correct){
            std::cout << "Not correct case: " << i << "\n"
                      << "FCL: " << fcl_distance << " -> " << fcl_correct <<  "\n"
                      << "Jolt: " << jolt_distance << " -> " << jolt_correct << "\n"
                      << "Bullet: " << bullet_distance << " -> " << bullet_correct << "\n";
        }
    }

    return 0;
}