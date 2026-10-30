use std::fs;
use std::path::Path;

use glam::{dvec3, DMat4, dmat4, dvec4, DVec3, DVec4};
use serde_json::Value;

use crate::{colliders::Collider};

pub fn load_test_file(path: &str) -> Vec<(Collider, Collider, f64)> {
    let contents = fs::read_to_string(path).unwrap();
    let json_data: Value = serde_json::from_str(&contents).unwrap();

    let data_dir = Path::new(path)
        .parent()
        .expect("Test file path has no parent directory");

    let mut result: Vec<(Collider, Collider, f64)> = Vec::new();

    for json_obj in json_data.as_array().unwrap() {

        let collider1 = parse_collider(&json_obj["collider1"], data_dir);
        let collider2 = parse_collider(&json_obj["collider2"], data_dir);
        let distance = json_obj["distance"].as_f64().unwrap();

        result.push((collider1, collider2, distance))
    }

    result
}

pub fn parse_collider(json_obj: &Value, data_dir: &Path) -> Collider {
    match json_obj["type"].as_str().unwrap() {
        "Sphere" => {
            let collider2origin = parse_mat4(&json_obj["collider2origin"]);

            let radius = json_obj["radius"].as_f64().unwrap();

            Collider::new_sphere(collider2origin, radius)
        }
        "Capsule" => {
            let collider2origin = parse_mat4(&json_obj["collider2origin"]);

            let radius = json_obj["radius"].as_f64().unwrap();
            let height = json_obj["height"].as_f64().unwrap();

            Collider::new_capsule(collider2origin, radius, height)
        }
        "Cylinder" => {
            let collider2origin = parse_mat4(&json_obj["collider2origin"]);

            let radius = json_obj["radius"].as_f64().unwrap();
            let height = json_obj["height"].as_f64().unwrap();

            Collider::new_cylinder(collider2origin, radius, height)
        }
        "Box" => {
            let collider2origin = parse_mat4(&json_obj["collider2origin"]);

            let size = parse_vec3(&json_obj["size"]);

            Collider::new_box(collider2origin, size)
        }
        "Mesh" => {
            let collider2origin = parse_mat4(&json_obj["collider2origin"]);

            let mesh_path = json_obj["mesh_path"]
                .as_str()
                .expect("Mesh 'mesh_path' must be a string");

            let full_path = data_dir.join(mesh_path);
            let (vertices, triangles) = load_obj(&full_path)
                .unwrap_or_else(|e|
                    panic!("Failed to load OBJ file '{}': {}", full_path.display(), e)
                );

            Collider::new_mesh(collider2origin, vertices, triangles)
        }
        &_ => todo!()
    }
}

fn load_obj(path: &Path) -> Result<(Vec<DVec3>, Vec<[usize; 3]>), String> {
    let contents = fs::read_to_string(path)
        .map_err(|e| format!("Could not read file: {}", e))?;

    let mut vertices: Vec<DVec3> = Vec::new();
    let mut triangles: Vec<[usize; 3]> = Vec::new();

    for line in contents.lines() {
        if let Some(rest) = line.strip_prefix("v ") {
            let coords: Vec<f64> = rest
                .split_whitespace()
                .map(|s| s.parse::<f64>().map_err(|_| {
                    format!("Expected float in vertex, got '{}'", s)
                }))
                .collect::<Result<_, _>>()?;

            if coords.len() != 3 {
                return Err(format!(
                    "Expected 3 floats after 'v', got {}: '{}'",
                    coords.len(), line
                ));
            }
            vertices.push(dvec3(coords[0], coords[1], coords[2]));

        } else if let Some(rest) = line.strip_prefix("f ") {
            let idx: Vec<usize> = rest
                .split_whitespace()
                .map(|s| s.parse::<usize>().map_err(|_| {
                    format!("Expected integer index in face, got '{}'", s)
                }))
                .collect::<Result<_, _>>()?;

            if idx.len() != 3 {
                return Err(format!(
                    "Expected 3 indices after 'f', got {}: '{}'",
                    idx.len(), line
                ));
            }

            // OBJ indices are 1-based
            let triangle = [idx[0] - 1, idx[1] - 1, idx[2] - 1];
            triangles.push(triangle);
        }
    }

    if vertices.is_empty() {
        return Err("OBJ file contains no vertex data ('v' lines)".to_string());
    }
    if triangles.is_empty() {
        return Err("OBJ file contains no face data ('f' lines)".to_string());
    }

    Ok((vertices, triangles))
}

fn parse_vec3(json_obj: &Value) -> DVec3 {
    dvec3(
        json_obj[0].as_f64().unwrap(),
        json_obj[1].as_f64().unwrap(),
        json_obj[2].as_f64().unwrap(),
    )
}

fn parse_vec4(json_obj: &Value) -> DVec4 {
    dvec4(
        json_obj[0].as_f64().unwrap(),
        json_obj[1].as_f64().unwrap(),
        json_obj[2].as_f64().unwrap(),
        json_obj[3].as_f64().unwrap(),
    )
}

fn parse_mat4(json_obj: &Value) -> DMat4 {
    dmat4(
        parse_vec4(&json_obj[0]),
        parse_vec4(&json_obj[1]),
        parse_vec4(&json_obj[2]),
        parse_vec4(&json_obj[3]),
    ).transpose()
}

#[cfg(test)]
mod test{
    use glam::dvec3;
    use serde_json::Value;

    use crate::{colliders::ColliderType, json_loder::{parse_collider, load_test_file}, gjk::GJKNesterov};

    #[test]
    fn test_parse_json_collider() {
        // data_dir is only used for Mesh colliders, so just use "" as path here:
        let data_dir = std::path::Path::new("");

        let json_obj: Value = serde_json::from_str(r#"
        {
            "type": "Sphere",
            "center": [
                1.0,
                0.0,
                0.0
            ],
            "radius": 10.0
        }"#).unwrap();

        let collider = parse_collider(&json_obj, data_dir);
        assert!(collider.typ == ColliderType::Sphere);
        assert!(collider.center == dvec3(1.0, 0.0, 0.0));
        assert!(collider.radius == 10.0);


        let json_obj: Value = serde_json::from_str(r#"
        {
            "type": "Capsule",
            "center": [
                0.0,
                1.0,
                2.0
            ],
            "radius": 1.0,
            "height": 2.0
        }"#).unwrap();

        let collider = parse_collider(&json_obj, data_dir);
        assert!(collider.typ == ColliderType::Capsule);
        // assert!(collider.center == vec3(0.0, 1.0, 2.0)); TODO
        assert!(collider.radius == 1.0);
        assert!(collider.height == 2.0);


        let json_obj: Value = serde_json::from_str(r#"
        {
            "type": "Cylinder",
            "center": [
                5.0,
                1.0,
                0.0
            ],
            "radius": 10.0,
            "height": 3.0
        }"#).unwrap();

        let collider = parse_collider(&json_obj, data_dir);
        assert!(collider.typ == ColliderType::Cylinder);
        // assert!(collider.center == vec3(5.0, 1.0, 0.0)); TODO
        assert!(collider.radius == 10.0);
        assert!(collider.height == 3.0);
    }
}

