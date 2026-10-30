use std::time::Duration;
use criterion::{black_box, criterion_group, criterion_main, Criterion, SamplingMode};
use compare::{ncollide::{get_cases, distance}, load_data};

fn bench_ncollide(c: &mut Criterion) {

    let gjk_cases = load_data();
    let ncollide_cases = get_cases(&gjk_cases);


    run_benchmark(c, "ncollide_distance", || {
        for (collider0, collider1, _) in ncollide_cases.iter() {
            black_box(distance(collider0, collider1));
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
    targets = bench_ncollide
}
criterion_main!(benches);