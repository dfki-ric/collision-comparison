use cgmath::{Matrix4};
use collision::{algorithm::minkowski::GJK3, primitive::{Primitive3, Sphere, Capsule, Cylinder, Cuboid}};
use compare::{collision::get_cases, load_data};
use criterion::{criterion_group, criterion_main, Criterion};


fn original_benchmark_test_file(c: &mut Criterion) {

    let gjk_cases = load_data();
    let collision_cases = get_cases(&gjk_cases);

    let gjk = GJK3::new();

    c.bench_function("collision-rs_intersect_gjk", |b| b.iter(|| 
        for i in 0..collision_cases.len() {
            let ((transform_0, shape_0), (transform_1, shape_1), _) = &collision_cases[i];
            gjk.intersect(shape_0, transform_0, shape_1, transform_1);
        }
    ));
}

fn original_distance_benchmark_test_file(c: &mut Criterion) {

    let gjk_cases = load_data();
    let collision_cases = get_cases(&gjk_cases);

    let gjk = GJK3::new();

    c.bench_function("collision-rs_distance_gjk", |b| b.iter(|| 
        for i in 0..collision_cases.len() {
            let ((transform_0, shape_0), (transform_1, shape_1), _) = &collision_cases[i];
            gjk.distance(shape_0, transform_0, shape_1, transform_1);
        }
    ));
}

fn nasterov_benchmark_test_file(c: &mut Criterion) {

    let gjk_cases = load_data();
    let collision_cases = get_cases(&gjk_cases);

    let gjk = GJK3::new();

    c.bench_function("collision-rs_nasterov_gjk", |b| b.iter(|| 
        for i in 0..collision_cases.len() {
            let ((transform_0, shape_0), (transform_1, shape_1), _) = &collision_cases[i];
            gjk.distance_nesterov_accelerated(shape_0, transform_0, shape_1, transform_1);
        }
    ));
}

criterion_group!(benches, original_benchmark_test_file, original_distance_benchmark_test_file, nasterov_benchmark_test_file);
criterion_main!(benches);


