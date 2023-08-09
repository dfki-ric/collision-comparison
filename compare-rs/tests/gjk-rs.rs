use cgmath::{AbsDiffEq, AbsDiff};
use compare::{load_data, collision::get_cases};
use gjk::gjk::GJKNesterov;

#[test]
fn test_gjk() {

    let cases = load_data();

    for (i, (collider1, collider2, dist) )in cases.iter().enumerate() {
        let mut gjk = GJKNesterov::new(None, 1e-6);
        let (_, test_dist, _ )= gjk.distance_nesterov_accelerated(collider1, collider2, 100);

        if AbsDiff::default().epsilon(0.1).ne(dist, &test_dist){
            println!("Gjk-rs: Index: {} with dist {} not correct. Dist Result: {}", i, dist, test_dist);
            
        }
    }
}


