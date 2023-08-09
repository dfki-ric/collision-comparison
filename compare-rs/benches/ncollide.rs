use criterion::{criterion_group, criterion_main, Criterion};
use gjk::colliders::ColliderType;
use ncollide3d::{query, shape::Shape};
use compare::{ncollide::get_cases, load_data};

fn bench_ncollide(c: &mut Criterion) {

    let gjk_cases = load_data();
    let ncollide_cases = get_cases(&gjk_cases);


    c.bench_function("ncollide_distance", |b| b.iter(|| 
        for (collider0, collider1, _) in ncollide_cases.iter() {
            
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