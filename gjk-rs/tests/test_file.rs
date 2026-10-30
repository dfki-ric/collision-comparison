use gjk::{json_loder::load_test_file, gjk::GJKNesterov};

#[test]
fn test_run_test_file() {

    let path = "../data/test_data.json";
    let test_data = load_test_file(path);

    let mut iteration_sum = 0;

    for (i, data) in test_data.iter().enumerate() {
        println!("Case: {i}");

        let mut gjk = GJKNesterov::new(None, 1e-6);

        let (_, test_distance, iterations) = gjk.distance_nesterov_accelerated(&data.0, &data.1, 100);

        assert!((test_distance - data.2).abs() < 0.01);

        println!("Interations: {iterations}"); 
        iteration_sum += iterations;
    }

    println!("Interations per Case: {:?}", (iteration_sum as f32) / test_data.len() as f32); 
}
