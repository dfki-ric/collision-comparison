use std::time::Duration;
use criterion::{criterion_group, criterion_main, Criterion};
use gjk::colliders::ColliderType;
use ncollide3d::{query, shape::Shape};
use compare::{ncollide::get_cases, load_data};

fn bench_ncollide(c: &mut Criterion) {

    let gjk_cases = load_data();
    let ncollide_cases = get_cases(&gjk_cases);


    c.bench_function("ncollide_distance", |b| b.iter(|| 
        for (collider0, collider1, _) in ncollide_cases.iter() {
            let shape0: &dyn Shape<f64> = match collider0.typ {
                ColliderType::Sphere   => &collider0.ball,
                ColliderType::Box      => &collider0.cuboid,
                ColliderType::Cylinder => &collider0.capsule,  // we cannot use cylinder here as Cylinder does not implement the "Shape" trait
                ColliderType::Capsule  => &collider0.capsule,
                ColliderType::Mesh     => &collider0.mesh,
            };

            let shape1: &dyn Shape<f64> = match collider1.typ {
                ColliderType::Sphere   => &collider1.ball,
                ColliderType::Box      => &collider1.cuboid,
                ColliderType::Cylinder => &collider1.capsule,  // we cannot use cylinder here as Cylinder does not implement the "Shape" trait
                ColliderType::Capsule  => &collider1.capsule,
                ColliderType::Mesh     => &collider1.mesh,
            };

            query::distance(&collider0.transform, shape0, &collider1.transform, shape1);
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