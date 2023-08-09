use cgmath::AbsDiff;
use collision::algorithm::minkowski::GJK3;
use compare::{load_data, collision::get_cases};

#[test]
fn test_collision() {

    let gjk_cases = load_data();
    let collision_cases = get_cases(&gjk_cases);

    let gjk = GJK3::new();

    for (i, ((transform_0, shape_0), (transform_1, shape_1), dist) )in collision_cases.iter().enumerate() {
       
        let result = gjk.distance(shape_0, transform_0, shape_1, transform_1);
        let test_dist = result.unwrap_or(0.0);
    
        if AbsDiff::default().epsilon(0.1).ne(dist, &test_dist){
            println!("Collision-rs: Index: {} with dist {} not correct. Dist Result: {}", i, dist, test_dist);
        }
    }
}