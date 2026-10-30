use std::time::Duration;
use compare::load_data;
use criterion::{black_box, criterion_group, criterion_main, Criterion, SamplingMode};
use gjk::{colliders::Collider, gjk::GJKNesterov};


fn test_nesterov(collider1: &Collider, collider2: &Collider) {
    let mut gjk = GJKNesterov::new(None, 1e-6);
    black_box(gjk.distance_nesterov_accelerated(collider1, collider2, 100));
}

fn bench_nesterov_accelerated(c: &mut Criterion) {

    let cases = load_data();

    run_benchmark(c, "gjk-rs_nasterov_gjk", || {
        for (_i, data) in cases.iter().enumerate() {
            test_nesterov(&data.0, &data.1);
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
    targets = bench_nesterov_accelerated
}
criterion_main!(benches);