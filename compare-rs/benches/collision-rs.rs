use std::time::Duration;
use collision::{algorithm::minkowski::GJK3};
use compare::{collision::get_cases, load_data};
use criterion::{black_box, criterion_group, criterion_main, Criterion, SamplingMode};


fn original_benchmark_test_file(c: &mut Criterion) {

    let gjk_cases = load_data();
    let collision_cases = get_cases(&gjk_cases);

    let gjk = GJK3::new();

    run_benchmark(c, "collision-rs_intersect_gjk", || {
        for i in 0..collision_cases.len() {
            let ((transform_0, shape_0), (transform_1, shape_1), _) = &collision_cases[i];
            black_box(gjk.intersect(shape_0, transform_0, shape_1, transform_1));
        }
    });
}

fn original_distance_benchmark_test_file(c: &mut Criterion) {

    let gjk_cases = load_data();
    let collision_cases = get_cases(&gjk_cases);

    let gjk = GJK3::new();

    run_benchmark(c, "collision-rs_distance_gjk", || {
        for i in 0..collision_cases.len() {
            let ((transform_0, shape_0), (transform_1, shape_1), _) = &collision_cases[i];
            black_box(gjk.distance(shape_0, transform_0, shape_1, transform_1));
        }
    });
}

fn nasterov_benchmark_test_file(c: &mut Criterion) {

    let gjk_cases = load_data();
    let collision_cases = get_cases(&gjk_cases);

    let gjk = GJK3::new();

    run_benchmark(c, "collision-rs_nasterov_gjk", || {
        for i in 0..collision_cases.len() {
            let ((transform_0, shape_0), (transform_1, shape_1), _) = &collision_cases[i];
            black_box(gjk.distance_nesterov_accelerated(shape_0, transform_0, shape_1, transform_1));
        }
    });
}

fn fast_config() -> Criterion {
    // Same number of repetitions for all implementations (see compare-cpp/main.cpp): 10 warm-up runs over all cases
    // of the case file (see run_benchmark), and 10 samples with exactly one run each (flat sampling, set for the
    // benchmark group; the measurement time is too short for more). Criterion's own warm-up stops after its first run.
    // The result is the median of the 10 runs.
    Criterion::default()
        .warm_up_time(Duration::from_nanos(1))
        .measurement_time(Duration::from_nanos(1))
        .sample_size(10)
}

/// 10 warm-up runs, then the measurement with flat sampling, which criterion only supports for benchmark groups.
/// The results are stored in target/criterion/<name>/all_cases.
fn run_benchmark<F: FnMut()>(c: &mut Criterion, name: &str, mut run_all_cases: F) {
    for _ in 0..10 {
        run_all_cases();
    }
    let mut group = c.benchmark_group(name);
    group.sampling_mode(SamplingMode::Flat);
    group.bench_function("all_cases", |b| b.iter(|| run_all_cases()));
    group.finish();
}


criterion_group! {
    name = benches;
    config = fast_config();
    // collision-rs' GJK distance panics on some cases (degenerate simplex), which aborts this benchmark binary:
    // run it last, so that the other benchmarks still produce results
    targets = original_benchmark_test_file, nasterov_benchmark_test_file, original_distance_benchmark_test_file
}
criterion_main!(benches);


