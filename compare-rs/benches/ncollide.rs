use std::time::Duration;
use criterion::{criterion_group, criterion_main, Criterion};
use compare::{ncollide::{get_cases, distance}, load_data};

fn bench_ncollide(c: &mut Criterion) {

    let gjk_cases = load_data();
    let ncollide_cases = get_cases(&gjk_cases);


    c.bench_function("ncollide_distance", |b| b.iter(|| 
        for (collider0, collider1, _) in ncollide_cases.iter() {
            distance(collider0, collider1);
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
    targets = bench_ncollide
}
criterion_main!(benches);