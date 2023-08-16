
#include "collider.h"
#include "jolt.h"
#include "fcl.h"
#include "bullet.h"
#include "libccd.h"

#include <iostream>

#define ANKERL_NANOBENCH_IMPLEMENT
#include <nanobench.h>

using compare::Base::load_cases;
using compare::Base::Case;

using compare::FCL::FCLCase;
using compare::Jolt::JoltCase;
using compare::Bullet::BulletCase;
using compare::libccd::LibccdCase;

bool is_distance_correct(float test_dist, float base_dist){
    return (base_dist <= 0 && test_dist <= 0) || abs(base_dist - test_dist) < 0.1;
}

int main(){

    char* path = "../../data/nao_test_cases.json";

    compare::Jolt::init();

    int cases_length = 161;

    Case base_cases[cases_length];
    load_cases(path, &base_cases[0], cases_length);

    FCLCase fcl_cases[cases_length];
    compare::FCL::get_cases(&base_cases[0], &fcl_cases[0], cases_length);

    JoltCase jolt_cases[cases_length];
    compare::Jolt::get_cases(&base_cases[0], &jolt_cases[0], cases_length);

    BulletCase bullet_cases[cases_length];
    compare::Bullet::get_cases(&base_cases[0], &bullet_cases[0], cases_length);

    LibccdCase libccd_cases[cases_length];
    compare::libccd::get_cases(&base_cases[0], &libccd_cases[0], cases_length);

#ifdef NDEBUG
    std::cout << "\n\n";

    ankerl::nanobench::Bench().minEpochIterations(1000).run("libccd intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::libccd::get_intersection(libccd_cases[i]);
        }
    });

    ankerl::nanobench::Bench().minEpochIterations(1000).run("Jolt intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::Jolt::get_intersection(jolt_cases[i]);
        }
    });

    ankerl::nanobench::Bench().minEpochIterations(1000).run("FCL distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_distance(fcl_cases[i]);
        }
    });

    ankerl::nanobench::Bench().minEpochIterations(1000).run("Bullet distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::Bullet::get_distance(bullet_cases[i]);
        }
    });


	return 0;
#endif

    for (int i = 0; i < cases_length; i++) {

        float base_distance = compare::Base::get_distance(&base_cases[i]);
        float fcl_distance = compare::FCL::get_distance(fcl_cases[i]);
        float bullet_distance = compare::Bullet::get_distance(bullet_cases[i]);

        bool base_intersect   = base_distance <= 0;
        bool libccd_intersect = compare::libccd::get_intersection(libccd_cases[i]);
        bool fcl_intersect    = fcl_distance <= 0;
        bool jolt_intersect   = compare::Jolt::get_intersection(jolt_cases[i]);
        bool bullet_intersect = bullet_distance <= 0;

        bool libccd_correct = libccd_intersect == base_intersect;
        bool fcl_correct = is_distance_correct(fcl_distance, base_distance);
        bool jolt_correct = jolt_intersect == base_intersect;
        bool bullet_correct = is_distance_correct(bullet_distance, base_distance);

        if (!libccd_correct || !fcl_correct || !jolt_correct || !bullet_correct){
            std::cout << "Not correct case: " << i << "\n"
                      << "distance3d Intersect: " << base_intersect   << " Distance: " << base_distance   << "\n"
                      << "libccd     Intersect: " << libccd_intersect << " Distance: " << "/"             << " -> " << libccd_correct << "\n"
                      << "FCL        Intersect: " << fcl_intersect    << " Distance: " << fcl_distance    << " -> " << fcl_correct    <<  "\n"
                      << "Jolt       Intersect: " << jolt_intersect   << " Distance: " << "/"             << " -> " << jolt_correct   << "\n"
                      << "Bullet     Intersect: " << bullet_intersect << " Distance: " << bullet_distance << " -> " << bullet_correct << "\n";
        }
    }

    return 0;
}