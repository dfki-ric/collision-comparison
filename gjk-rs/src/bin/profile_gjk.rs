use gjk::{json_loder::load_test_file, gjk::GJKNesterov};

fn main() {

    let path = "../data/test_data.json";
    let test_data = load_test_file(path);

    for data in test_data {
        let mut gjk = GJKNesterov::new(None, 1e-6);
        gjk.distance_nesterov_accelerated(&data.0, &data.1, 100);
    }
}

