use cgmath::{Quaternion, Vector3, Decomposed, BaseFloat, Rotation3, Rad, Transform, Matrix4};
use collision::{algorithm::minkowski::GJK3, primitive::{Primitive3, Sphere, Capsule, Cylinder, Cube, Cuboid}};
use criterion::{criterion_group, criterion_main, Criterion, BenchmarkId};
use gjk::{json_loder::load_test_file, colliders::{Collider, ColliderType}};

fn collider_to_transform_and_primitive(collider: &Collider) -> (Matrix4<f64>, Primitive3<f64>){
    let transform = Matrix4::<f64>::new(
        collider.transform.x_axis.x, collider.transform.x_axis.y, collider.transform.x_axis.z, collider.center.x,
        collider.transform.y_axis.x, collider.transform.y_axis.y, collider.transform.y_axis.z, collider.center.y,
        collider.transform.z_axis.x, collider.transform.z_axis.y, collider.transform.z_axis.z, collider.center.z,
        0.0, 0.0, 0.0, 1.0
    );

    let primitive = match collider.typ {
        x if x == ColliderType::Sphere => {
            Primitive3::Sphere(Sphere::new(collider.radius))
        },
        x if x == ColliderType::Capluse => {
            Primitive3::Capsule(Capsule::new(collider.height * 0.5, collider.radius))
        },
        x if x == ColliderType::Cylinder => {
            Primitive3::Cylinder(Cylinder::new(collider.height * 0.5, collider.radius))
        },    
        x if x == ColliderType::Box => {
            Primitive3::Cuboid(Cuboid::new(collider.size.x, collider.size.y, collider.size.z))
        },    
        _ => todo!(),
    };

    (transform, primitive)
}

fn load_data() -> Vec<((Matrix4<f64>, Primitive3<f64>), (Matrix4<f64>, Primitive3<f64>))>{
    let path = "../data/nao_test_cases.json";
    let test_data = load_test_file(path);

    let mut cases = Vec::new();
    for (collider0, collider1, dist) in test_data.iter() {
        cases.push((collider_to_transform_and_primitive(collider0), collider_to_transform_and_primitive(collider1)))
    }

    cases
}

fn original_benchmark_test_file(c: &mut Criterion) {

    let cases = load_data();

    let gjk = GJK3::new();

    c.bench_function("collision-rs_intersect_gjk", |b| b.iter(|| 
        for i in 0..cases.len() {
            let ((transform_0, shape_0), (transform_1, shape_1)) = &cases[i];
            gjk.intersect(shape_0, transform_0, shape_1, transform_1);
        }
    ));
}

fn original_distance_benchmark_test_file(c: &mut Criterion) {

    let cases = load_data();

    let gjk = GJK3::new();

    c.bench_function("collision-rs_distance_gjk", |b| b.iter(|| 
        for i in 0..cases.len() {
            let ((transform_0, shape_0), (transform_1, shape_1)) = &cases[i];
            gjk.distance(shape_0, transform_0, shape_1, transform_1);
        }
    ));
}

fn nasterov_benchmark_test_file(c: &mut Criterion) {

    let cases = load_data();

    let gjk = GJK3::new();

    c.bench_function("collision-rs_nasterov_gjk", |b| b.iter(|| 
        for i in 0..cases.len() {
            let ((transform_0, shape_0), (transform_1, shape_1)) = &cases[i];
            gjk.distance_nesterov_accelerated(shape_0, transform_0, shape_1, transform_1);
        }
    ));
}

criterion_group!(benches, original_benchmark_test_file, original_distance_benchmark_test_file, nasterov_benchmark_test_file);
criterion_main!(benches);


