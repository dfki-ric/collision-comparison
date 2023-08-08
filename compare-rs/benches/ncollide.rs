use criterion::{criterion_group, criterion_main, Criterion, BenchmarkId};
use gjk::{colliders::{Collider, ColliderType}, json_loder::load_test_file};
use ncollide3d::{query::{distance, self}, shape::{Cuboid, Ball, Cylinder, Capsule, Shape}, na::{Vector3, Isometry3, self}};

struct Collider2{
    ball: Ball<f64>,
    cuboid: Cuboid<f64>,
    cylinder: Cylinder<f64>,
    capluse: Capsule<f64>,

    typ: ColliderType,
    transform: Isometry3<f64>
}


fn get_collider(collider: &Collider) -> Collider2 {
    let matrix = na::Matrix3::new(
        collider.transform.col(0)[0], collider.transform.col(0)[1], collider.transform.col(0)[2],
        collider.transform.col(1)[0], collider.transform.col(1)[1], collider.transform.col(1)[2],
        collider.transform.col(2)[0], collider.transform.col(2)[1], collider.transform.col(2)[2]);

    let rotation = na::Rotation3::from_matrix(&matrix);
    let pos = na::Vector3::new(collider.center[0], collider.center[1], collider.center[2]);
    let transform = Isometry3::new(pos, *rotation.axis_angle().unwrap().0);

    Collider2{
        ball: Ball::new(collider.radius),
        cuboid: Cuboid::new(na::Vector3::new(collider.size[0] / 2.0, collider.size[1] / 2.0, collider.size[2] / 2.0)),
        cylinder: Cylinder::new(collider.height / 2.0, collider.radius),
        capluse: Capsule::new(collider.height / 2.0, collider.radius),
        transform: transform,
        typ: collider.typ,
    }   
}

fn bench_ncollide(c: &mut Criterion) {

    let path = "../data/nao_test_cases.json";
    let cases = load_test_file(path);

    let mut cases2 = Vec::new();
    for (collider0, collider1, _) in cases.iter() {
        cases2.push((get_collider(collider0), get_collider(collider1)))
    }

    c.bench_function("ncollide_distance", |b| b.iter(|| 
        for (collider0, collider1) in cases2.iter() {
            
            let shape0: &dyn Shape<f64> = if collider0.typ == ColliderType::Sphere {
                &collider0.ball
            }else if collider0.typ == ColliderType::Box {
                &collider0.cuboid
            }else {
                &collider0.capluse
            };

            let shape1: &dyn Shape<f64> = if collider1.typ == ColliderType::Sphere {
                &collider1.ball
            }else if collider1.typ == ColliderType::Box {
                &collider1.cuboid
            }else {
                &collider1.capluse
            };

            query::distance(&collider0.transform, shape0, &collider1.transform, shape1);
        }
    ));
}

criterion_group!(benches, bench_ncollide);
criterion_main!(benches);