use glam::{DVec3, DMat4, Vec4Swizzles, DMat3};
use collision::primitive::{Primitive3, Sphere};

pub mod random;
pub mod support_point;

#[derive(PartialEq, Clone, Copy)]
pub enum ColliderType {
    Sphere,
    Capsule,
    Cylinder,
    Box,
    Mesh
}

pub struct Collider {
    pub typ: ColliderType,

    pub transform: DMat3,
    pub transform_transposed: DMat3,
    pub center: DVec3,

    pub radius: f64,
    pub height: f64,
    pub size: DVec3,

    pub vertices: Vec<DVec3>,
    pub triangles: Vec<[usize; 3]>,
    pub convex_mesh: Primitive3<f64>,
}

impl Collider {

    pub fn new_sphere(collider2origin: DMat4, radius: f64) -> Self {
        let transform = DMat3::from_mat4(collider2origin);

        Self {
            typ: ColliderType::Sphere,
            transform,
            transform_transposed: transform.transpose(),
            center: Self::get_center_from_collider2origin(&collider2origin), 
            radius: radius, 
            height: 0.0,
            size: DVec3::ZERO,
            vertices: Vec::new(),
            triangles: Vec::new(),
            convex_mesh: Primitive3::Sphere(Sphere::new(0.0)),
        }
    }

    pub fn new_capsule(collider2origin: DMat4, radius: f64, height: f64) -> Self {
        let transform = DMat3::from_mat4(collider2origin);

        Self {
            typ: ColliderType::Capsule,
            transform,
            transform_transposed: transform.transpose(),
            center: Self::get_center_from_collider2origin(&collider2origin),
            radius: radius,
            height: height,
            size: DVec3::ZERO,
            vertices: Vec::new(),
            triangles: Vec::new(),
            convex_mesh: Primitive3::Sphere(Sphere::new(0.0)),
        }
    }

    pub fn new_cylinder(collider2origin: DMat4, radius: f64, height: f64) -> Self {
        let transform = DMat3::from_mat4(collider2origin);

        Self {
            typ: ColliderType::Cylinder,
            transform,
            transform_transposed: transform.transpose(),
            center: Self::get_center_from_collider2origin(&collider2origin),
            radius: radius,
            height: height,
            size: DVec3::ZERO,
            vertices: Vec::new(),
            triangles: Vec::new(),
            convex_mesh: Primitive3::Sphere(Sphere::new(0.0)),
        }
    }

    pub fn new_box(collider2origin: DMat4, size: DVec3) -> Self {
        let transform = DMat3::from_mat4(collider2origin);

        Self {
            typ: ColliderType::Box,
            transform,
            transform_transposed: transform.transpose(),
            center: Self::get_center_from_collider2origin(&collider2origin),
            radius: 0.0,
            height: 0.0,
            size: size,
            vertices: Vec::new(),
            triangles: Vec::new(),
            convex_mesh: Primitive3::Sphere(Sphere::new(0.0)),
        }
    }

    pub fn new_mesh(collider2origin: DMat4, vertices: Vec<DVec3>, triangles: Vec<[usize; 3]>) -> Self {
        let transform = DMat3::from_mat4(collider2origin);

        let vertices_cgmath: Vec<cgmath::Point3<f64>> = vertices
            .iter()
            .map(|v| cgmath::Point3::new(v.x, v.y, v.z))
            .collect();

        // let faces_cgmath: Vec<(usize, usize, usize)> = triangles
        //     .iter()
        //     .map(|t| (t[0], t[1], t[2]))
        //     .collect();

        let convex_mesh = Primitive3::ConvexPolyhedron(
            // it would be better to use ::new_with_faces() here to utilise
            // the more efficient support function, but it seems that
            // the hill-climbing support function often runs
            // into infinite loops when used on some (more complex) meshes

            // collision::primitive::ConvexPolyhedron::new_with_faces(&vertices_cgmath, &faces_cgmath)
            collision::primitive::ConvexPolyhedron::new(&vertices_cgmath)
        );

        Self {
            typ: ColliderType::Mesh,
            transform,
            transform_transposed: transform.transpose(),
            center: Self::get_center_from_collider2origin(&collider2origin),
            radius: 0.0,
            height: 0.0,
            size: DVec3::ZERO,
            vertices,
            triangles,
            convex_mesh,
        }
    }

    fn get_center_from_collider2origin(collider2origin: &DMat4 ) -> DVec3 {
        collider2origin.w_axis.xyz()
    }

}