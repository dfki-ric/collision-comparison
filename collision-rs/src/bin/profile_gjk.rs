use cgmath::{Quaternion, Vector3, Decomposed, BaseFloat, Rotation3, Rad};
use collision::{algorithm::minkowski::GJK3, primitive::Primitive3};
use rand::{rngs::StdRng, Rng, distributions::uniform::{SampleUniform, SampleRange}, SeedableRng};

fn random_transform<S, R>(
    rng: &mut impl Rng,
    pos_range: R,
    angle_range: R,
) -> Decomposed<Vector3<S>, Quaternion<S>>
where
    S: BaseFloat + SampleUniform,
    R: SampleRange<S> + Clone,
{
    Decomposed {
        disp: Vector3::<S>::new(
            rng.gen_range(pos_range.to_owned()),
            rng.gen_range(pos_range.to_owned()),
            rng.gen_range(pos_range.to_owned()),
        ),
        rot: Quaternion::from_angle_z(Rad(rng.gen_range(angle_range))),
        scale: S::one(),
    }
}

fn main() {

    let mut rng = StdRng::seed_from_u64(42);
    let size_range = 0.0..100.0;
    let pos_range = 0.0..500.0;
    let angle_range = 0.0..360.0;

    let gjk = GJK3::new();

    for _i in 0..100 {
        let transform_0 = random_transform(&mut rng, pos_range.to_owned(), angle_range.to_owned());
        let transform_1 = random_transform(&mut rng, pos_range.to_owned(), angle_range.to_owned());

        let shape_0 = Primitive3::new_random(&mut rng, size_range.to_owned());
        let shape_1 = Primitive3::new_random(&mut rng, size_range.to_owned());

        gjk.intersect(&shape_0, &transform_0, &shape_1, &transform_1);
        gjk.distance_nesterov_accelerated(&shape_0, &transform_0, &shape_1, &transform_1);
    }
}
