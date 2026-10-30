use cgmath::AbsDiff;
use compare::{load_data, ncollide::get_cases};
use gjk::colliders::ColliderType;
use ncollide3d::{shape::Shape, query};

#[test]
fn test_collision() {

    let gjk_cases = load_data();
    let ncollide_cases = get_cases(&gjk_cases);

    for (i, (collider0, collider1, dist) )in ncollide_cases.iter().enumerate() {
        let shape0: &dyn Shape<f64> = match collider0.typ {
            ColliderType::Sphere   => &collider0.ball,
            ColliderType::Box      => &collider0.cuboid,
            ColliderType::Cylinder => &collider0.capsule, // we cannot use cylinder here as Cylinder does not implement the "Shape" trait
            ColliderType::Capsule  => &collider0.capsule,
            ColliderType::Mesh     => &collider0.mesh,
        };

        let shape1: &dyn Shape<f64> = match collider1.typ {
            ColliderType::Sphere   => &collider1.ball,
            ColliderType::Box      => &collider1.cuboid,
            ColliderType::Cylinder => &collider1.capsule, // we cannot use cylinder here as Cylinder does not implement the "Shape" trait
            ColliderType::Capsule  => &collider1.capsule,
            ColliderType::Mesh     => &collider1.mesh,
        };

        let test_dist = query::distance(&collider0.transform, shape0, &collider1.transform, shape1);

        if AbsDiff::default().epsilon(0.1).ne(dist, &test_dist){
            println!("NCollide: Index: {} with dist {} not correct. Dist Result: {}", i, dist, test_dist);
        }
    }
}