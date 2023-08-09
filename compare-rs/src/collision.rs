use cgmath::Matrix4;
use collision::primitive::{Primitive3, Sphere, Capsule, Cylinder, Cuboid};
use gjk::colliders::{Collider, ColliderType};

pub fn get_collider(collider: &Collider) -> (Matrix4<f64>, Primitive3<f64>){
    let transform = Matrix4::<f64>::new(
        collider.transform.col(0)[0], collider.transform.col(0)[1], collider.transform.col(0)[2], 0.0,
        collider.transform.col(1)[0], collider.transform.col(1)[1], collider.transform.col(1)[2], 0.0,
        collider.transform.col(2)[0], collider.transform.col(2)[1], collider.transform.col(2)[2], 0.0,
        collider.center[0], collider.center[1], collider.center[2], 1.0
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


pub fn get_cases(cases: &Vec<(Collider, Collider, f64)>) -> Vec<((Matrix4<f64>, Primitive3<f64>), (Matrix4<f64>, Primitive3<f64>), f64)> {
    let mut collision_cases = Vec::new();
    for (collider0, collider1, dist) in cases.iter() {
        collision_cases.push((get_collider(collider0), get_collider(collider1), dist.to_owned()))
    }

    collision_cases
}