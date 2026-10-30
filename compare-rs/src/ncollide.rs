use gjk::colliders::{ColliderType, Collider};
use ncollide3d::{shape::{Ball, Cuboid, Cylinder, Capsule}, na::{Isometry3, self}};
use ncollide3d::shape::{ConvexHull, Shape, SupportMap};
use ncollide3d::query;

pub struct NcollideCollider{
    pub ball: Ball<f64>,
    pub cuboid: Cuboid<f64>,
    pub cylinder: Cylinder<f64>,
    pub capsule: Capsule<f64>,
    pub mesh: ConvexHull<f64>,

    pub typ: ColliderType,
    pub transform: Isometry3<f64>
}

pub fn get_collider(collider: &Collider) -> NcollideCollider {
    // na::Matrix3::new takes the entries row by row, collider.transform.col(c)[r] is row r, column c
    let matrix = na::Matrix3::new(
        collider.transform.col(0)[0], collider.transform.col(1)[0], collider.transform.col(2)[0],
        collider.transform.col(0)[1], collider.transform.col(1)[1], collider.transform.col(2)[1],
        collider.transform.col(0)[2], collider.transform.col(1)[2], collider.transform.col(2)[2]);

    let rotation = na::Rotation3::from_matrix(&matrix);
    let pos = na::Vector3::new(collider.center[0], collider.center[1], collider.center[2]);

    // Isometry3::new expects the rotation axis scaled by the rotation angle
    let mut transform = Isometry3::new(pos, rotation.scaled_axis());

    // ncollide's cylinders and capsules are aligned with the y axis, the data uses the z axis:
    // rotate by 90 degrees about x, which maps y to z
    if collider.typ == ColliderType::Cylinder || collider.typ == ColliderType::Capsule {
        transform = transform * Isometry3::rotation(na::Vector3::x() * std::f64::consts::FRAC_PI_2);
    }

    NcollideCollider{
        ball: Ball::new(collider.radius),
        cuboid: Cuboid::new(na::Vector3::new(collider.size[0] / 2.0, collider.size[1] / 2.0, collider.size[2] / 2.0)),
        cylinder: Cylinder::new(collider.height / 2.0, collider.radius),
        capsule: Capsule::new(collider.height / 2.0, collider.radius),
        mesh: if collider.typ == ColliderType::Mesh
        {
            ConvexHull::try_from_points(
                & collider.vertices
                    .iter()
                    .map( | v| na::Point3::new(v.x, v.y, v.z))
                    .collect:: < Vec<_ > > ()
            ).expect("ConvexHull::try_from_points failed")
        } else {
            let dummy_points = Vec::from([
                na::Point3::new(0.0,0.0,0.0),
                na::Point3::new(1.0,0.0,0.0),
                na::Point3::new(0.0,1.0,0.0),
            ]);
            ConvexHull::try_from_points(&dummy_points).expect("ConvexHull::try_from_points failed")
        },
        transform: transform,
        typ: collider.typ,
    }   
}

fn get_shape(collider: &NcollideCollider) -> &dyn Shape<f64> {
    match collider.typ {
        ColliderType::Sphere   => &collider.ball,
        ColliderType::Box      => &collider.cuboid,
        ColliderType::Capsule  => &collider.capsule,
        ColliderType::Mesh     => &collider.mesh,
        ColliderType::Cylinder => unreachable!("Cylinder does not implement the Shape trait"),
    }
}

fn get_support_map(collider: &NcollideCollider) -> &dyn SupportMap<f64> {
    match collider.typ {
        ColliderType::Sphere   => &collider.ball,
        ColliderType::Box      => &collider.cuboid,
        ColliderType::Cylinder => &collider.cylinder,
        ColliderType::Capsule  => &collider.capsule,
        ColliderType::Mesh     => &collider.mesh,
    }
}

/// Distance between two colliders, used by benches/ncollide.rs.
#[inline]
pub fn distance(collider0: &NcollideCollider, collider1: &NcollideCollider) -> f64 {
    if collider0.typ == ColliderType::Cylinder || collider1.typ == ColliderType::Cylinder {
        // Cylinder does not implement the Shape trait, so query::distance() cannot be used. For two support maps,
        // query::distance() calls query::distance_support_map_support_map() anyway, so we call it directly.
        return query::distance_support_map_support_map(&collider0.transform, get_support_map(collider0),
                                                       &collider1.transform, get_support_map(collider1));
    }
    query::distance(&collider0.transform, get_shape(collider0), &collider1.transform, get_shape(collider1))
}

pub fn get_cases(cases: &Vec<(Collider, Collider, f64)>) -> Vec<(NcollideCollider, NcollideCollider, f64)> {
    let mut ncollide_cases = Vec::new();
    for (collider0, collider1, dist) in cases.iter() {
        ncollide_cases.push((get_collider(collider0), get_collider(collider1), dist.to_owned()))
    }

    ncollide_cases
}