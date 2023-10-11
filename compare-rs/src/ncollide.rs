use gjk::colliders::{ColliderType, Collider};
use ncollide3d::{shape::{Ball, Cuboid, Cylinder, Capsule}, na::{Isometry3, self}};


pub struct NcollideCollider{
    pub ball: Ball<f64>,
    pub cuboid: Cuboid<f64>,
    pub cylinder: Cylinder<f64>,
    pub capluse: Capsule<f64>,

    pub typ: ColliderType,
    pub transform: Isometry3<f64>
}

pub fn get_collider(collider: &Collider) -> NcollideCollider {
    let matrix = na::Matrix3::new(
        collider.transform.col(0)[0], collider.transform.col(0)[1], collider.transform.col(0)[2],
        collider.transform.col(1)[0], collider.transform.col(1)[1], collider.transform.col(1)[2],
        collider.transform.col(2)[0], collider.transform.col(2)[1], collider.transform.col(2)[2]);

    let rotation = na::Rotation3::from_matrix(&matrix);
    let pos = na::Vector3::new(collider.center[0], collider.center[1], collider.center[2]);

    let axis_angle = if rotation.axis_angle().is_some() {
            *rotation.axis_angle().unwrap().0} 
        else {
            na::Vector3::new(0.0, 0.0, 0.0)
        };
    let transform = Isometry3::new(pos, axis_angle);

    NcollideCollider{
        ball: Ball::new(collider.radius),
        cuboid: Cuboid::new(na::Vector3::new(collider.size[0] / 2.0, collider.size[1] / 2.0, collider.size[2] / 2.0)),
        cylinder: Cylinder::new(collider.height / 2.0, collider.radius),
        capluse: Capsule::new(collider.height / 2.0, collider.radius),
        transform: transform,
        typ: collider.typ,
    }   
}

pub fn get_cases(cases: &Vec<(Collider, Collider, f64)>) -> Vec<(NcollideCollider, NcollideCollider, f64)> {
    let mut ncollide_cases = Vec::new();
    for (collider0, collider1, dist) in cases.iter() {
        ncollide_cases.push((get_collider(collider0), get_collider(collider1), dist.to_owned()))
    }

    ncollide_cases
}