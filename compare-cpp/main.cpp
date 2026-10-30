
#include "collider.h"
#include "jolt.h"
#include "fcl.h"
#include "bullet.h"
#include "libccd.h"
#include "openGJK.h"

#include <iostream>

#define ANKERL_NANOBENCH_IMPLEMENT
#include <nanobench.h>

using compare::Base::load_cases;
using compare::Base::Case;

using compare::FCL::FCLCase;
using compare::Jolt::JoltCase;
using compare::Bullet::BulletCase;
using compare::libccd::LibccdCase;
using compare::OpenGJK::OpenGJKCase;

bool is_distance_correct(float test_dist, float base_dist){
    return (base_dist <= 0 && test_dist <= 0) || abs(base_dist - test_dist) < 0.1;
}

void gen(std::string const& typeName, char const* mustacheTemplate, ankerl::nanobench::Bench const& bench) {

}

int main(){

    const char* path = "../data/current.json";

    compare::Jolt::init();

    Case base_cases[200];
    const int cases_length = load_cases(path, &base_cases[0], 200);

    std::vector<FCLCase> fcl_cases_nesterov(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov[0], cases_length, false);

    std::vector<FCLCase> fcl_cases_nesterov_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_lin_support[0], cases_length, true);

    std::vector<FCLCase> fcl_cases_nesterov_intersection(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_intersection[0], cases_length, false);

    std::vector<FCLCase> fcl_cases_nesterov_intersection_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_intersection_lin_support[0], cases_length, true);

    std::vector<FCLCase> fcl_cases_default(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default[0], cases_length, false);

    std::vector<FCLCase> fcl_cases_default_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default_lin_support[0], cases_length, true);

    std::vector<FCLCase> fcl_cases_default_intersection(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default_intersection[0], cases_length, false);

    std::vector<FCLCase> fcl_cases_default_intersection_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default_intersection_lin_support[0], cases_length, true);

    std::vector<JoltCase> jolt_cases(cases_length);
    compare::Jolt::get_cases(&base_cases[0], &jolt_cases[0], cases_length);

    std::vector<JoltCase> jolt_cases_dist(cases_length);
    compare::Jolt::get_cases(&base_cases[0], &jolt_cases_dist[0], cases_length);

    std::vector<BulletCase> bullet_cases(cases_length);
    compare::Bullet::get_cases(&base_cases[0], &bullet_cases[0], cases_length);

    std::vector<LibccdCase> libccd_cases(cases_length);
    compare::libccd::get_cases(&base_cases[0], &libccd_cases[0], cases_length, false);

    std::vector<LibccdCase> libccd_cases_lin_support(cases_length);
    compare::libccd::get_cases(&base_cases[0], &libccd_cases_lin_support[0], cases_length, true);

    std::vector<OpenGJKCase> openGJK_cases(cases_length);
    compare::OpenGJK::get_cases(&base_cases[0], &openGJK_cases[0], cases_length);

    std::vector<OpenGJKCase> openGJK_cases_lin_support(cases_length);
    compare::OpenGJK::get_cases(&base_cases[0], &openGJK_cases_lin_support[0], cases_length);

#define NDEBUG
#ifdef NDEBUG
    std::cout << "\n\n";

    ankerl::nanobench::Bench bench;
    bench.minEpochIterations(10);

    bench.run("libccd intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::libccd::get_intersection(libccd_cases[i]);
        }
    });

    bench.run("libccd intersection linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::libccd::get_intersection(libccd_cases_lin_support[i]);
        }
    });

    bench.run("Jolt intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::Jolt::get_intersection(jolt_cases[i]);
        }
    });

    bench.run("Jolt distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::Jolt::get_distance(jolt_cases_dist[i]);
        }
    });

    bench.run("FCL distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_distance_nesterov(fcl_cases_nesterov[i]);
        }
    });

    bench.run("FCL distance linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_distance_nesterov(fcl_cases_nesterov_lin_support[i]);
        }
    });

    bench.run("FCL intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection[i]);
        }
    });

    bench.run("FCL intersection linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection_lin_support[i]);
        }
    });

    bench.run("FCL distance defaultGJK", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_distance_default(fcl_cases_default[i]);
        }
    });

    bench.run("FCL distance defaultGJK linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_distance_default(fcl_cases_default_lin_support[i]);
        }
    });

    bench.run("FCL intersection defaultGJK", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_intersection_default(fcl_cases_default_intersection[i]);
        }
    });

    bench.run("FCL intersection defaultGJK linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::FCL::get_intersection_default(fcl_cases_default_intersection_lin_support[i]);
        }
    });

    bench.run("Bullet distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::Bullet::get_distance(bullet_cases[i]);
        }
    });

    bench.run("openGJK distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::OpenGJK::get_distance(openGJK_cases[i], false);
        }
    });

    bench.run("openGJK distance linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            compare::OpenGJK::get_distance(openGJK_cases_lin_support[i], true);
        }
    });

    std::ofstream renderOut("./cpp_result.json");
    ankerl::nanobench::render(ankerl::nanobench::templates::json(), bench, renderOut);

#else
    for (int i = 0; i < cases_length; i++)
    {
        std::cout
        << "\n\n--===[ Case  " << i << " ]===--\n"
        << "[Reference] distance3d Distance: " << compare::Base::get_distance(&base_cases[i]) << "\n"
        << "Intersection Algorithms:" << "\n"
        << "\tlibccd                Intersect: " << compare::libccd::get_intersection(libccd_cases[i]) << "\n"
        << "\tlibccd (lin supp.)    Intersect: " << compare::libccd::get_intersection(libccd_cases_lin_support[i]) << "\n"
        << "\tHPP-FCL               Intersect: " << compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection[i]) << "\n"
        << "\tHPP-FCL (lin supp.)   Intersect: " << compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection_lin_support[i]) << "\n"
        << "\tJolt                  Intersect: " << compare::Jolt::get_intersection(jolt_cases[i]) << "\n"
        << "Distance Algorithms:" << "\n"
        << "\tHPP-FCL               Distance: " << compare::FCL::get_distance_nesterov(fcl_cases_nesterov[i]) << "\n"
        << "\tHPP-FCL (lin supp.)   Distance: " << compare::FCL::get_distance_nesterov(fcl_cases_nesterov_lin_support[i]) << "\n"
        << "\tBullet                Distance: " << compare::Bullet::get_distance(bullet_cases[i]) << "\n"
        << "\tJolt Distance         Distance: " << compare::Jolt::get_distance(jolt_cases_dist[i]) << "\n"
        << "\tOpenGJK               Distance: " << compare::OpenGJK::get_distance(openGJK_cases[i], false) << "\n"
        << "\tOpenGJK (lin supp.)   Distance: " << compare::OpenGJK::get_distance(openGJK_cases_lin_support[i], true) << "\n";
    }
#endif

    return 0;
}