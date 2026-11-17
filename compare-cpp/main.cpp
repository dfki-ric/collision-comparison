
#include "collider.h"
#include "jolt.h"
#include "fcl.h"
#include "hppfcl.h"
#include "fcl_original.h"
#include "mujoco.h"
#include "bullet.h"
#include "libccd.h"
#include "openGJK.h"

#include <cstdlib>
#include <iostream>
#include <regex>

#define ANKERL_NANOBENCH_IMPLEMENT
#include <nanobench.h>

using compare::Base::load_cases;
using compare::Base::Case;
using compare::Base::SupportMode;

using compare::FCL::FCLCase;
using compare::FCLOriginal::FCLOriginalCase;
using compare::MuJoCo::MuJoCoCase;
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

    // The linear support function is only used for meshes (primitive shapes have their own support functions), so
    // its variants are only benchmarked for case files with meshes
    bool has_mesh = false;
    for (int i = 0; i < cases_length; i++) {
        has_mesh = has_mesh || base_cases[i].collider0.type == compare::Base::Mesh
                            || base_cases[i].collider1.type == compare::Base::Mesh;
    }

    std::vector<FCLCase> fcl_cases_nesterov(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov[0], cases_length, SupportMode::HillClimbing);

    std::vector<FCLCase> fcl_cases_nesterov_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<FCLCase> fcl_cases_nesterov_extremes(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<FCLCase> fcl_cases_nesterov_intersection(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_intersection[0], cases_length, SupportMode::HillClimbing);

    std::vector<FCLCase> fcl_cases_nesterov_intersection_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_intersection_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<FCLCase> fcl_cases_nesterov_intersection_extremes(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_intersection_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<FCLCase> fcl_cases_default(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default[0], cases_length, SupportMode::HillClimbing);

    std::vector<FCLCase> fcl_cases_default_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<FCLCase> fcl_cases_default_extremes(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<FCLCase> fcl_cases_default_intersection(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default_intersection[0], cases_length, SupportMode::HillClimbing);

    std::vector<FCLCase> fcl_cases_default_intersection_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default_intersection_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<FCLCase> fcl_cases_default_intersection_extremes(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_default_intersection_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<FCLCase> fcl_cases_polyak(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_polyak[0], cases_length, SupportMode::HillClimbing);

    std::vector<FCLCase> fcl_cases_polyak_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_polyak_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<FCLCase> fcl_cases_polyak_extremes(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_polyak_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<FCLCase> fcl_cases_polyak_intersection(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_polyak_intersection[0], cases_length, SupportMode::HillClimbing);

    std::vector<FCLCase> fcl_cases_polyak_intersection_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_polyak_intersection_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<FCLCase> fcl_cases_polyak_intersection_extremes(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_polyak_intersection_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<FCLCase> fcl_cases_nesterov_normalized(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_normalized[0], cases_length, SupportMode::HillClimbing);

    std::vector<FCLCase> fcl_cases_nesterov_normalized_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_normalized_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<FCLCase> fcl_cases_nesterov_normalized_extremes(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_normalized_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<FCLCase> fcl_cases_nesterov_normalized_intersection(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_normalized_intersection[0], cases_length, SupportMode::HillClimbing);

    std::vector<FCLCase> fcl_cases_nesterov_normalized_intersection_lin_support(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_normalized_intersection_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<FCLCase> fcl_cases_nesterov_normalized_intersection_extremes(cases_length);
    compare::FCL::get_cases(&base_cases[0], &fcl_cases_nesterov_normalized_intersection_extremes[0], cases_length, SupportMode::CachedExtremes);

    // the HPP-FCL fork of the earlier runs (hppfcl.h), for the comparison with Coal
    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_default(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_default[0], cases_length, SupportMode::HillClimbing);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_default_extremes(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_default_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_default_linear(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_default_linear[0], cases_length, SupportMode::Linear);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_default_intersection(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_default_intersection[0], cases_length, SupportMode::HillClimbing);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_default_intersection_extremes(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_default_intersection_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_default_intersection_linear(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_default_intersection_linear[0], cases_length, SupportMode::Linear);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_nesterov(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_nesterov[0], cases_length, SupportMode::HillClimbing);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_nesterov_extremes(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_nesterov_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_nesterov_linear(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_nesterov_linear[0], cases_length, SupportMode::Linear);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_nesterov_intersection(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_nesterov_intersection[0], cases_length, SupportMode::HillClimbing);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_nesterov_intersection_extremes(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_nesterov_intersection_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<compare::HPPFCL::HPPFCLCase> hppfcl_nesterov_intersection_linear(cases_length);
    compare::HPPFCL::get_cases(&base_cases[0], &hppfcl_nesterov_intersection_linear[0], cases_length, SupportMode::Linear);

    std::vector<FCLOriginalCase> fcl_original_cases(cases_length);
    compare::FCLOriginal::get_cases(&base_cases[0], &fcl_original_cases[0], cases_length);

    std::vector<MuJoCoCase> mujoco_cases(cases_length);
    compare::MuJoCo::get_cases(&base_cases[0], &mujoco_cases[0], cases_length);

    std::vector<MuJoCoCase> mujoco_cases_lin_support(cases_length);
    compare::MuJoCo::get_cases(&base_cases[0], &mujoco_cases_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<MuJoCoCase> mujoco_cases_hill_climbing(cases_length);
    compare::MuJoCo::get_cases(&base_cases[0], &mujoco_cases_hill_climbing[0], cases_length, SupportMode::HillClimbing);

    std::vector<JoltCase> jolt_cases(cases_length);
    compare::Jolt::get_cases(&base_cases[0], &jolt_cases[0], cases_length);

    std::vector<JoltCase> jolt_cases_dist(cases_length);
    compare::Jolt::get_cases(&base_cases[0], &jolt_cases_dist[0], cases_length);

    std::vector<BulletCase> bullet_cases(cases_length);
    compare::Bullet::get_cases(&base_cases[0], &bullet_cases[0], cases_length);

    std::vector<LibccdCase> libccd_cases(cases_length);
    compare::libccd::get_cases(&base_cases[0], &libccd_cases[0], cases_length, SupportMode::HillClimbing);

    std::vector<LibccdCase> libccd_cases_lin_support(cases_length);
    compare::libccd::get_cases(&base_cases[0], &libccd_cases_lin_support[0], cases_length, SupportMode::Linear);

    std::vector<LibccdCase> libccd_cases_extremes(cases_length);
    compare::libccd::get_cases(&base_cases[0], &libccd_cases_extremes[0], cases_length, SupportMode::CachedExtremes);

    std::vector<LibccdCase> libccd_cases_adaptive(cases_length);
    compare::libccd::get_cases(&base_cases[0], &libccd_cases_adaptive[0], cases_length, SupportMode::Adaptive);

    std::vector<OpenGJKCase> openGJK_cases(cases_length);
    compare::OpenGJK::get_cases(&base_cases[0], &openGJK_cases[0], cases_length);

    std::vector<OpenGJKCase> openGJK_cases_lin_support(cases_length);
    compare::OpenGJK::get_cases(&base_cases[0], &openGJK_cases_lin_support[0], cases_length);

// Release builds (CMAKE_BUILD_TYPE=Release, see scripts/compile/compile_compare_release.sh) define NDEBUG and run
// the benchmark, debug builds (scripts/compile/compile_compare_debug.sh) print the results of all algorithms instead.
#ifdef NDEBUG
    std::cout << "\n\n";

    ankerl::nanobench::Bench bench;
    // Same number of repetitions for all implementations: 10 warm-up runs and 10 runs (epochs) over all cases
    // of the case file. The result is the median of the 10 runs. One warm-up run is not enough: the first
    // measured runs after it are still considerably slower.
    bench.warmup(10).epochs(10).epochIterations(1);

    // Only the benchmarks whose name matches the regular expression in the environment variable BENCHMARK_FILTER
    // are run (default: all), see scripts/benchmarks/benchmark_dataset.sh
    const char* filter_env = std::getenv("BENCHMARK_FILTER");
    const std::regex filter(filter_env != nullptr && filter_env[0] != '\0' ? filter_env : ".*");
    auto run = [&](const char* name, auto&& benchmark) {
        if (std::regex_search(name, filter)) {
            bench.run(name, benchmark);
        }
    };

    run("libccd intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::libccd::get_intersection(libccd_cases[i]));
        }
    });

    if (has_mesh) run("libccd intersection linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::libccd::get_intersection(libccd_cases_lin_support[i]));
        }
    });

    if (has_mesh) run("libccd intersection cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::libccd::get_intersection(libccd_cases_extremes[i]));
        }
    });

    if (has_mesh) run("libccd intersection adaptive support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::libccd::get_intersection(libccd_cases_adaptive[i]));
        }
    });

    run("Jolt intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::Jolt::get_intersection(jolt_cases[i]));
        }
    });

    run("Jolt distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::Jolt::get_distance(jolt_cases_dist[i]));
        }
    });

    run("Coal distance nesterov", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_nesterov(fcl_cases_nesterov[i]));
        }
    });

    if (has_mesh) run("Coal distance nesterov linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_nesterov(fcl_cases_nesterov_lin_support[i]));
        }
    });

    if (has_mesh) run("Coal distance nesterov cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_nesterov(fcl_cases_nesterov_extremes[i]));
        }
    });

    run("Coal intersection nesterov", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection[i]));
        }
    });

    if (has_mesh) run("Coal intersection nesterov linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection_lin_support[i]));
        }
    });

    if (has_mesh) run("Coal intersection nesterov cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection_extremes[i]));
        }
    });

    run("Coal distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_default(fcl_cases_default[i]));
        }
    });

    if (has_mesh) run("Coal distance linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_default(fcl_cases_default_lin_support[i]));
        }
    });

    if (has_mesh) run("Coal distance cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_default(fcl_cases_default_extremes[i]));
        }
    });

    run("Coal intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_default(fcl_cases_default_intersection[i]));
        }
    });

    if (has_mesh) run("Coal intersection linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_default(fcl_cases_default_intersection_lin_support[i]));
        }
    });

    if (has_mesh) run("Coal intersection cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_default(fcl_cases_default_intersection_extremes[i]));
        }
    });

    run("Coal distance polyak", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_polyak(fcl_cases_polyak[i]));
        }
    });

    if (has_mesh) run("Coal distance polyak linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_polyak(fcl_cases_polyak_lin_support[i]));
        }
    });

    if (has_mesh) run("Coal distance polyak cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_polyak(fcl_cases_polyak_extremes[i]));
        }
    });

    run("Coal intersection polyak", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_polyak(fcl_cases_polyak_intersection[i]));
        }
    });

    if (has_mesh) run("Coal intersection polyak linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_polyak(fcl_cases_polyak_intersection_lin_support[i]));
        }
    });

    if (has_mesh) run("Coal intersection polyak cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_polyak(fcl_cases_polyak_intersection_extremes[i]));
        }
    });

    run("Coal distance nesterov normalized", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_nesterov_normalized(fcl_cases_nesterov_normalized[i]));
        }
    });

    if (has_mesh) run("Coal distance nesterov normalized linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_nesterov_normalized(fcl_cases_nesterov_normalized_lin_support[i]));
        }
    });

    if (has_mesh) run("Coal distance nesterov normalized cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_distance_nesterov_normalized(fcl_cases_nesterov_normalized_extremes[i]));
        }
    });

    run("Coal intersection nesterov normalized", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_nesterov_normalized(fcl_cases_nesterov_normalized_intersection[i]));
        }
    });

    if (has_mesh) run("Coal intersection nesterov normalized linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_nesterov_normalized(fcl_cases_nesterov_normalized_intersection_lin_support[i]));
        }
    });

    if (has_mesh) run("Coal intersection nesterov normalized cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCL::get_intersection_nesterov_normalized(fcl_cases_nesterov_normalized_intersection_extremes[i]));
        }
    });

    run("HPP-FCL distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_distance_default(hppfcl_default[i]));
        }
    });

    if (has_mesh) run("HPP-FCL distance cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_distance_default(hppfcl_default_extremes[i]));
        }
    });

    if (has_mesh) run("HPP-FCL distance linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_distance_default(hppfcl_default_linear[i]));
        }
    });

    run("HPP-FCL intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_intersection_default(hppfcl_default_intersection[i]));
        }
    });

    if (has_mesh) run("HPP-FCL intersection cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_intersection_default(hppfcl_default_intersection_extremes[i]));
        }
    });

    if (has_mesh) run("HPP-FCL intersection linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_intersection_default(hppfcl_default_intersection_linear[i]));
        }
    });

    run("HPP-FCL distance nesterov", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_distance_nesterov(hppfcl_nesterov[i]));
        }
    });

    if (has_mesh) run("HPP-FCL distance nesterov cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_distance_nesterov(hppfcl_nesterov_extremes[i]));
        }
    });

    if (has_mesh) run("HPP-FCL distance nesterov linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_distance_nesterov(hppfcl_nesterov_linear[i]));
        }
    });

    run("HPP-FCL intersection nesterov", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_intersection_nesterov(hppfcl_nesterov_intersection[i]));
        }
    });

    if (has_mesh) run("HPP-FCL intersection nesterov cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_intersection_nesterov(hppfcl_nesterov_intersection_extremes[i]));
        }
    });

    if (has_mesh) run("HPP-FCL intersection nesterov linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::HPPFCL::get_intersection_nesterov(hppfcl_nesterov_intersection_linear[i]));
        }
    });

    run("FCL original distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::FCLOriginal::get_distance(fcl_original_cases[i]));
        }
    });

    run("MuJoCo intersection", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::MuJoCo::get_intersection(mujoco_cases[i]));
        }
    });

    if (has_mesh) run("MuJoCo intersection linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::MuJoCo::get_intersection(mujoco_cases_lin_support[i]));
        }
    });

    if (has_mesh) run("MuJoCo intersection hill climbing", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::MuJoCo::get_intersection(mujoco_cases_hill_climbing[i]));
        }
    });

    run("MuJoCo distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::MuJoCo::get_distance(mujoco_cases[i]));
        }
    });

    if (has_mesh) run("MuJoCo distance linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::MuJoCo::get_distance(mujoco_cases_lin_support[i]));
        }
    });

    if (has_mesh) run("MuJoCo distance hill climbing", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::MuJoCo::get_distance(mujoco_cases_hill_climbing[i]));
        }
    });

    run("Bullet distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::Bullet::get_distance(bullet_cases[i]));
        }
    });

    run("openGJK distance", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::OpenGJK::get_distance(openGJK_cases[i], SupportMode::HillClimbing));
        }
    });

    if (has_mesh) run("openGJK distance linear support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::OpenGJK::get_distance(openGJK_cases_lin_support[i], SupportMode::Linear));
        }
    });

    if (has_mesh) run("openGJK distance cached extremes", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::OpenGJK::get_distance(openGJK_cases[i], SupportMode::CachedExtremes));
        }
    });

    if (has_mesh) run("openGJK distance adaptive support", [&] {
        for (int i = 0; i < cases_length; i++) {
            ankerl::nanobench::doNotOptimizeAway(compare::OpenGJK::get_distance(openGJK_cases[i], SupportMode::Adaptive));
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
        << "\tlibccd (extremes)     Intersect: " << compare::libccd::get_intersection(libccd_cases_extremes[i]) << "\n"
        << "\tlibccd (adaptive)     Intersect: " << compare::libccd::get_intersection(libccd_cases_adaptive[i]) << "\n"
        << "\tCoal Nest.              Intersect: " << compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection[i]) << "\n"
        << "\tCoal Nest.(lin supp.)   Intersect: " << compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection_lin_support[i]) << "\n"
        << "\tCoal Nest.(extremes)    Intersect: " << compare::FCL::get_intersection_nesterov(fcl_cases_nesterov_intersection_extremes[i]) << "\n"
        << "\tJolt                  Intersect: " << compare::Jolt::get_intersection(jolt_cases[i]) << "\n"
        << "\tMuJoCo                Intersect: " << compare::MuJoCo::get_intersection(mujoco_cases[i]) << "\n"
        << "\tMuJoCo (lin supp.)    Intersect: " << compare::MuJoCo::get_intersection(mujoco_cases_lin_support[i]) << "\n"
        << "\tMuJoCo (hill climb.)  Intersect: " << compare::MuJoCo::get_intersection(mujoco_cases_hill_climbing[i]) << "\n"
        << "Distance Algorithms:" << "\n"
        << "\tCoal Nest.              Distance: " << compare::FCL::get_distance_nesterov(fcl_cases_nesterov[i]) << "\n"
        << "\tCoal Nest.(lin supp.)   Distance: " << compare::FCL::get_distance_nesterov(fcl_cases_nesterov_lin_support[i]) << "\n"
        << "\tCoal Nest.(extremes)    Distance: " << compare::FCL::get_distance_nesterov(fcl_cases_nesterov_extremes[i]) << "\n"
        << "\tFCL (original)        Distance: " << compare::FCLOriginal::get_distance(fcl_original_cases[i]) << "\n"
        << "\tMuJoCo                Distance: " << compare::MuJoCo::get_distance(mujoco_cases[i]) << "\n"
        << "\tMuJoCo (lin supp.)    Distance: " << compare::MuJoCo::get_distance(mujoco_cases_lin_support[i]) << "\n"
        << "\tMuJoCo (hill climb.)  Distance: " << compare::MuJoCo::get_distance(mujoco_cases_hill_climbing[i]) << "\n"
        << "\tBullet                Distance: " << compare::Bullet::get_distance(bullet_cases[i]) << "\n"
        << "\tJolt Distance         Distance: " << compare::Jolt::get_distance(jolt_cases_dist[i]) << "\n"
        << "\tOpenGJK               Distance: " << compare::OpenGJK::get_distance(openGJK_cases[i], SupportMode::HillClimbing) << "\n"
        << "\tOpenGJK (lin supp.)   Distance: " << compare::OpenGJK::get_distance(openGJK_cases_lin_support[i], SupportMode::Linear) << "\n"
        << "\tOpenGJK (extremes)    Distance: " << compare::OpenGJK::get_distance(openGJK_cases[i], SupportMode::CachedExtremes) << "\n"
        << "\tOpenGJK (adaptive)    Distance: " << compare::OpenGJK::get_distance(openGJK_cases[i], SupportMode::Adaptive) << "\n";
    }
#endif

    return 0;
}