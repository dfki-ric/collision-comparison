use std::time::Duration;
use compare::load_data;
use criterion::{criterion_group, criterion_main, Criterion};
use gjk::{colliders::Collider, gjk::GJKNesterov};


fn test_nesterov(collider1: &Collider, collider2: &Collider) {
    let mut gjk = GJKNesterov::new(None, 1e-6);
    gjk.distance_nesterov_accelerated(collider1, collider2, 100);
}

fn bench_nesterov_accelerated(c: &mut Criterion) {

    let cases = load_data();

    c.bench_function("gjk-rs_nasterov_gjk", |b| b.iter(|| 
        for (_i, data) in cases.iter().enumerate() {
            test_nesterov(&data.0, &data.1);
        }
    ));
}

fn fast_config() -> Criterion {
    // Change some values to speed up benchmarking with minimal loss in data quality:
    Criterion::default()
        .warm_up_time(Duration::from_millis(1000)) // default: 3s
        .measurement_time(Duration::from_secs(2)) // default: 5s
        .sample_size(50) // default: 100
}


criterion_group! {
    name = benches;
    config = fast_config();
    targets = bench_nesterov_accelerated
}
criterion_main!(benches);