use std::ops::Neg;

use cgmath::{vec3, Array, BaseFloat, InnerSpace, Point3, Transform, Vector3, Zero, point3, EuclideanSpace};

use crate::{algorithm::minkowski::SupportPoint, Primitive};

use super::{simplex::Simplex, GJK3};

struct NesterovData<S>
where
    S: BaseFloat,
{
    alpha: S,
    omega: S,

    simplex: Simplex<Point3<S>>,
    ray: Vector3<S>,
    ray_len: S,
    ray_dir: Vector3<S>,

    support_point: SupportPoint<Point3<S>>,
}

impl<S> GJK3<S>
where
    S: BaseFloat,
{
    /// TODO
    pub fn distance_nesterov_accelerated<PL, PR, TL, TR>(
        &self,
        left: &PL,
        left_transform: &TL,
        right: &PR,
        right_transform: &TR,
    ) -> (Option<Simplex<Point3<S>>>, S, u32)
    where
        PL: Primitive<Point = Point3<S>>,
        PR: Primitive<Point = Point3<S>>,
        TL: Transform<Point3<S>>,
        TR: Transform<Point3<S>>,
    {
        let upper_bound = S::from(1000000000).unwrap();

        let mut use_nesterov_acceleration = true;
        let normalize_support_direction = false;

        let inflation = S::zero();

        let mut inside = false;
        let mut distance = S::zero();

        let left_pos = left_transform.transform_point(Point3::origin());
        let right_pos = right_transform.transform_point(Point3::origin());
        let guess = left_pos - right_pos;

        let mut data = NesterovData::new(Some(guess), self.distance_tolerance);

        let mut interations = 0;

        for i in 0..self.max_iterations {
            let k = i as f64;
            interations = i;

            if data.ray_len < self.distance_tolerance {
                distance = -inflation;
                inside = true;
                break;
            }

            if use_nesterov_acceleration {
                let momentum = S::from((k + 1.0) / (k + 3.0)).unwrap();
                let y = data.ray * momentum + data.support_point.v * (S::one() - momentum);
                data.ray_dir = data.ray_dir * momentum + y * (S::one() - momentum);

                if normalize_support_direction {
                    data.ray_dir = data.ray_dir.normalize();
                }
            } else {
                data.ray_dir = data.ray;
            }

            data.support_point = SupportPoint::<Point3<S>>::from_minkowski(
                left,
                left_transform,
                right,
                right_transform,
                &data.ray_dir.neg(),
            );
            data.simplex.push(data.support_point);

            data.omega = data.ray_dir.dot(data.support_point.v) / data.ray_dir.magnitude();
            if data.omega > upper_bound {
                distance = data.omega - inflation;
                inside = false;
                break;
            }

            if use_nesterov_acceleration {
                let frank_wolfe_duality_gap =
                    S::from(2.0).unwrap() * data.ray.dot(data.ray - data.support_point.v);
                if frank_wolfe_duality_gap - self.distance_tolerance <= S::zero() {
                    use_nesterov_acceleration = false;
                    data.simplex.pop();
                    continue;
                }
            }

            let cv_check_passed = self.check_convergence(&mut data);
            if i > 0 && cv_check_passed {
                data.simplex.pop();
                if use_nesterov_acceleration {
                    use_nesterov_acceleration = false;
                    continue;
                }
                distance = data.ray_len - inflation;

                if distance < self.distance_tolerance {
                    inside = true
                }
                break;
            }

            match data.simplex.len() {
                1 => {
                    data.ray = data.support_point.v;
                }
                2 => inside = self.project_line_origen(&mut data),
                3 => inside = self.project_triangle_origen(&mut data),
                4 => inside = self.project_tetra_to_origen(&mut data),
                _ => {}
            }

            if !inside {
                data.ray_len = data.ray.magnitude();
            }

            if inside || data.ray_len == S::zero() {
                distance = -inflation;
                inside = true;
                break;
            }
        }

        return (if inside { Some(data.simplex) } else { None }, distance ,interations);
    }

    fn check_convergence(&self, data: &mut NesterovData<S>) -> bool {
        data.alpha = data.alpha.max(data.omega);

        let diff = data.ray_len - data.alpha;

        return (diff - self.distance_tolerance * data.ray_len) <= S::zero();
    }

    fn origen_to_point(&self, data: &mut NesterovData<S>, a_index: usize, a: Vector3<S>) {
        data.ray = a;
        data.simplex[0] = data.simplex[a_index];
        data.simplex.truncate(1);
    }

    fn origen_to_segment(
        &self,
        data: &mut NesterovData<S>,
        a_index: usize,
        b_index: usize,
        a: Vector3<S>,
        b: Vector3<S>,
        ab: Vector3<S>,
        ab_dot_a0: S,
    ) {
        data.ray = (a * ab.dot(b) + b * ab_dot_a0) / ab.magnitude2();
        data.simplex[0] = data.simplex[b_index];
        data.simplex[1] = data.simplex[a_index];
        data.simplex.truncate(2);
    }

    fn origen_to_triangle(
        &self,
        data: &mut NesterovData<S>,
        a_index: usize,
        b_index: usize,
        c_index: usize,
        abc: Vector3<S>,
        abc_dot_a0: S,
    ) -> bool {
        if abc_dot_a0 == S::zero() {
            data.simplex[0] = data.simplex[c_index];
            data.simplex[1] = data.simplex[b_index];
            data.simplex[2] = data.simplex[a_index];
            data.simplex.truncate(3);

            data.ray = Vector3::from_value(S::zero());
            return true;
        }

        if abc_dot_a0 > S::zero() {
            data.simplex[0] = data.simplex[c_index];
            data.simplex[1] = data.simplex[b_index];
        } else {
            data.simplex[0] = data.simplex[b_index];
            data.simplex[1] = data.simplex[c_index];
        }

        data.simplex[2] = data.simplex[a_index];
        data.simplex.truncate(3);

        data.ray = abc * -abc_dot_a0 / abc.magnitude2();
        if abc == Vector3::zero() {
            data.ray = abc;
        }

        return false;
    }

    fn project_line_origen(&self, data: &mut NesterovData<S>) -> bool {
        let a_index = 1;
        let b_index = 0;

        let a = data.simplex[a_index].v;
        let b = data.simplex[b_index].v;

        let ab = b - a;
        let d = ab.dot(-a);

        if d == S::zero() {
            /* Two extremely unlikely cases:
             - AB is orthogonal to A: should never happen because it means the support
               function did not do any progress and GJK should have stopped.
             - A == origin
            In any case, A is the closest to the origin */
            self.origen_to_point(data, a_index, a);
            return a.is_zero();
        }

        if d < S::zero() {
            self.origen_to_point(data, a_index, a);
        } else {
            self.origen_to_segment(data, a_index, b_index, a, b, ab, d);
        }

        return false;
    }

    fn project_triangle_origen(&self, data: &mut NesterovData<S>) -> bool {
        let a_index = 2;
        let b_index = 1;
        let c_index = 0;

        let a = data.simplex[a_index].v;
        let b = data.simplex[b_index].v;
        let c = data.simplex[c_index].v;

        let ab = b - a;
        let ac = c - a;
        let abc = ab.cross(ac);

        let edge_ac2o = abc.cross(ac).dot(-a);

        let t_b = |data: &mut NesterovData<S>| {
            let towards_b = ab.dot(-a);
            if towards_b < S::zero() {
                self.origen_to_point(data, a_index, a);
            } else {
                self.origen_to_segment(data, a_index, b_index, a, b, ab, towards_b)
            }
        };

        if edge_ac2o >= S::zero() {
            let towards_c = ac.dot(-a);
            if towards_c >= S::zero() {
                self.origen_to_segment(data, a_index, b_index, a, b, ab, towards_c)
            } else {
                t_b(data);
            }
        } else {
            let edge_ab2o = ab.cross(abc).dot(-a);
            if edge_ab2o >= S::zero() {
                t_b(data);
            } else {
                return self.origen_to_triangle(data, a_index, b_index, c_index, abc, abc.dot(-a));
            }
        }

        return false;
    }

    fn project_tetra_to_origen(&self, data: &mut NesterovData<S>) -> bool {
        let a_index = 3;
        let b_index = 2;
        let c_index = 1;
        let d_index = 0;

        let a = data.simplex[a_index].v;
        let b = data.simplex[b_index].v;
        let c = data.simplex[c_index].v;
        let d = data.simplex[d_index].v;

        let aa = a.magnitude2();

        let da = d.dot(a);
        let db = d.dot(b);
        let dc = d.dot(c);
        let dd = d.dot(d);
        let da_aa = da - aa;

        let ca = c.dot(a);
        let cb = c.dot(b);
        let cc = c.dot(c);
        let cd = dc;
        let ca_aa = ca - aa;

        let ba = b.dot(a);
        let bb = b.dot(b);
        let bc = cb;
        let bd = db;
        let ba_aa = ba - aa;
        let ba_ca = ba - ca;
        let ca_da = ca - da;
        let da_ba = da - ba;

        let a_cross_b = a.cross(b);
        let a_cross_c = a.cross(c);

        let region_inside = |data: &mut NesterovData<S>| {
            data.ray = Vector3::zero();
            true
        };

        let region_abc = |data: &mut NesterovData<S>| {
            self.origen_to_triangle(
                data,
                a_index,
                b_index,
                c_index,
                (b - a).cross(c - a),
                -c.dot(a_cross_b),
            )
        };

        let region_acd = |data: &mut NesterovData<S>| {
            self.origen_to_triangle(
                data,
                a_index,
                c_index,
                d_index,
                (c - a).cross(d - a),
                -d.dot(a_cross_c),
            )
        };

        let region_adb = |data: &mut NesterovData<S>| {
            self.origen_to_triangle(
                data,
                a_index,
                d_index,
                b_index,
                (d - a).cross(b - a),
                d.dot(a_cross_b),
            )
        };

        let region_ab = |data: &mut NesterovData<S>| {
            self.origen_to_segment(data, a_index, b_index, a, b, b - a, -ba_aa)
        };

        let region_ac = |data: &mut NesterovData<S>| {
            self.origen_to_segment(data, a_index, c_index, a, c, c - a, -ca_aa)
        };

        let region_ad = |data: &mut NesterovData<S>| {
            self.origen_to_segment(data, a_index, d_index, a, d, d - a, -da_aa)
        };

        let region_a = |data: &mut NesterovData<S>| self.origen_to_point(data, a_index, a);

        if ba_aa <= S::zero() {
            if -d.dot(a_cross_b) <= S::zero() {
                if ba * da_ba + bd * ba_aa - bb * da_aa <= S::zero() {
                    if da_aa <= S::zero() {
                        if ba * ba_ca + bb * ca_aa - bc * ba_aa <= S::zero() {
                            region_abc(data);
                        } else {
                            region_ab(data);
                        }
                    } else {
                        if ba * ba_ca + bb * ca_aa - bc * ba_aa <= S::zero() {
                            if ca * ba_ca + cb * ca_aa - cc * ba_aa <= S::zero() {
                                if ca * ca_da + cc * da_aa - cd * ca_aa <= S::zero() {
                                    region_acd(data);
                                } else {
                                    region_ac(data);
                                }
                            } else {
                                region_abc(data);
                            }
                        } else {
                            region_ab(data);
                        }
                    }
                } else {
                    if da * da_ba + dd * ba_aa - db * da_aa <= S::zero() {
                        region_adb(data);
                    } else {
                        if ca * ca_da + cc * da_aa - cd * ca_aa <= S::zero() {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= S::zero() {
                                region_ad(data);
                            } else {
                                region_acd(data);
                            }
                        } else {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= S::zero() {
                                region_ad(data);
                            } else {
                                region_ac(data);
                            }
                        }
                    }
                }
            } else {
                if c.dot(a_cross_b) <= S::zero() {
                    if ba * ba_ca + bb * ca_aa - bc * ba_aa <= S::zero() {
                        if ca * ba_ca + cb * ca_aa - cc * ba_aa <= S::zero() {
                            if ca * ca_da + cc * da_aa - cd * ca_aa <= S::zero() {
                                region_acd(data);
                            } else {
                                region_ac(data);
                            }
                        } else {
                            region_abc(data);
                        }
                    } else {
                        region_ad(data);
                    }
                } else {
                    if d.dot(a_cross_c) <= S::zero() {
                        if ca * ca_da + cc * da_aa - cd * ca_aa <= S::zero() {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= S::zero() {
                                region_ad(data);
                            } else {
                                region_acd(data);
                            }
                        } else {
                            if ca_aa <= S::zero() {
                                region_ac(data);
                            } else {
                                region_ad(data);
                            }
                        }
                    } else {
                        return region_inside(data);
                    }
                }
            }
        } else {
            if ca_aa <= S::zero() {
                if d.dot(a_cross_c) <= S::zero() {
                    if da_aa <= S::zero() {
                        if ca * ca_da + cc * da_aa - cd * ca_aa <= S::zero() {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= S::zero() {
                                if da * da_ba + dd * ba_aa - db * da_aa <= S::zero() {
                                    region_adb(data);
                                } else {
                                    region_ad(data);
                                }
                            } else {
                                region_acd(data);
                            }
                        } else {
                            if ca * ba_ca + cb * ca_aa - cc * ba_aa <= S::zero() {
                                region_ac(data);
                            } else {
                                region_abc(data);
                            }
                        }
                    } else {
                        if ca * ba_ca + cb * ca_aa - cc * ba_aa <= S::zero() {
                            if ca * ca_da + cc * da_aa - cd * ca_aa <= S::zero() {
                                region_acd(data);
                            } else {
                                region_ac(data);
                            }
                        } else {
                            if c.dot(a_cross_b) <= S::zero() {
                                region_abc(data);
                            } else {
                                region_acd(data);
                            }
                        }
                    }
                } else {
                    if c.dot(a_cross_b) <= S::zero() {
                        if ca * ba_ca + cb * ca_aa - cc * ba_aa <= S::zero() {
                            region_ac(data);
                        } else {
                            region_abc(data);
                        }
                    } else {
                        if -d.dot(a_cross_b) <= S::zero() {
                            if da * da_ba + dd * ba_aa - db * da_aa <= S::zero() {
                                region_adb(data);
                            } else {
                                region_ad(data);
                            }
                        } else {
                            return region_inside(data);
                        }
                    }
                }
            } else {
                if da_aa <= S::zero() {
                    if -d.dot(a_cross_b) <= S::zero() {
                        if da * ca_da + dc * da_aa - dd * ca_aa <= S::zero() {
                            if da * da_ba + dd * ba_aa - db * da_aa <= S::zero() {
                                region_adb(data);
                            } else {
                                region_ad(data);
                            }
                        } else {
                            if d.dot(a_cross_c) <= S::zero() {
                                region_acd(data);
                            } else {
                                region_adb(data);
                            }
                        }
                    } else {
                        if d.dot(a_cross_c) <= S::zero() {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= S::zero() {
                                region_ad(data);
                            } else {
                                region_acd(data);
                            }
                        } else {
                            return region_inside(data);
                        }
                    }
                } else {
                    region_a(data);
                }
            }
        }

        return false;
    }
}

impl<S> NesterovData<S>
where
    S: BaseFloat,
{
    fn new(ray_guess: Option<Vector3<S>>, tolerance: S) -> Self {
        let simplex = Simplex::new();
        let mut ray = ray_guess.unwrap_or(vec3(S::one(), S::zero(), S::zero()));
        let mut ray_len = ray.magnitude();

        if ray_len < tolerance {
            ray = vec3(S::one(), S::zero(), S::zero());
            ray_len = S::one();
        }

        let ray_dir = ray;
        let support_point = SupportPoint{
            v: ray,
            sup_a: point3(ray.x, ray.y, ray.z),
            sup_b: point3(ray.x, ray.y, ray.z)
        };

        Self {
            alpha: S::zero(),
            omega: S::zero(),
            simplex,
            ray,
            ray_len,
            ray_dir,
            support_point,
        }
    }
}

#[cfg(test)]
mod tests {
    use std::fs;

    use crate::{
        algorithm::minkowski::GJK3,
        primitive::{Cuboid, Primitive3, Sphere},
    };
    use cgmath::{BaseFloat, Decomposed, Quaternion, Rad, Rotation3, Vector3};
    use rand::{
        distributions::uniform::{SampleRange, SampleUniform},
        rngs::StdRng,
        Rng, SeedableRng,
    };
    use serde_json::Value;

    fn transform_3d(
        x: f32,
        y: f32,
        z: f32,
        angle_z: f32,
    ) -> Decomposed<Vector3<f32>, Quaternion<f32>> {
        Decomposed {
            disp: Vector3::new(x, y, z),
            rot: Quaternion::from_angle_z(Rad(angle_z)),
            scale: 1.,
        }
    }

    #[test]
    fn test_gjk_nesterov_accelerated_exact_3d() {
        let shape = Cuboid::new(1., 1., 1.);
        let t = transform_3d(0., 0., 0., 0.);
        let gjk = GJK3::new();
        let (p, _, _) = gjk.distance_nesterov_accelerated(&shape, &t, &shape, &t);
        assert!(p.is_some());
    }

    #[test]
    fn test_gjk_nesterov_accelerated_sphere() {
        let shape = Sphere::new(1.);
        let t = transform_3d(0., 0., 0., 0.);
        let gjk = GJK3::new();
        let (p, _, _) = gjk.distance_nesterov_accelerated(&shape, &t, &shape, &t);
        assert!(p.is_some());
    }

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

    #[test]
    fn test_nesterov_accelerated_vs_original() {
        let iterations = 1000;

        let mut rng = StdRng::seed_from_u64(42);
        let size_range = 0.0..100.0;
        let pos_range = 0.0..500.0;
        let angle_range = 0.0..360.0;

        let gjk = GJK3::new();

        for i in 0..iterations {
            println!("Interation: {:?}", i);

            let transform_0 =
                random_transform(&mut rng, pos_range.to_owned(), angle_range.to_owned());
            let transform_1 =
                random_transform(&mut rng, pos_range.to_owned(), angle_range.to_owned());

            let shape_0 = Primitive3::new_random(&mut rng, size_range.to_owned());
            let shape_1 = Primitive3::new_random(&mut rng, size_range.to_owned());

            
            let test_p = gjk.intersect(&shape_0, &transform_0, &shape_1, &transform_1).0;
            
            if i == 791 {
                print!("Break")
            }
            
            let (p, _dist, _) = gjk.distance_nesterov_accelerated(&shape_0, &transform_0, &shape_1, &transform_1);

            assert!((p.is_some() == test_p.is_some()));
        }
    }

    #[test]
    fn test_file_assert_simplex() {
        test_file(true, false, false)
    }

    #[test]
    fn test_file_assert_dist() {
        test_file(false, true, false)
    }

    #[test]
    fn test_file_print_iterations() {
        test_file(false, false, true)
    }

    fn test_file(assert_p: bool, asstert_dist: bool, print_iterations: bool) {
        let path = "../data/test_data.json";
        let contents = fs::read_to_string(path).unwrap();

        let json_data: Value = serde_json::from_str(&contents).unwrap();

        let gjk = GJK3::new();

        let mut i = 0;
        let mut original_iteration_sum = 0;
        let mut nasterov_iteration_sum = 0;

        for json_obj in json_data.as_array().unwrap() {
            println!("Case: {:?}", i);

            let collider1 = &json_obj["collider1"];
            let collider2 = &json_obj["collider2"];
            let test_dist = json_obj["distance"].as_f64().unwrap();

            let (shape0, transform0) = Primitive3::<f64>::from_json(collider1);
            let (shape1, transform1) = Primitive3::<f64>::from_json(collider2);

            let (original_simplex, original_interations) = gjk.intersect(
                &shape0, 
                &transform0, 
                &shape1, 
                &transform1);

            let (nasterov_simplex, nasterov_distance, nasterov_interations) = gjk.distance_nesterov_accelerated(
                &shape0, 
                &transform0, 
                &shape1, 
                &transform1);
            
            if assert_p{
                assert!(original_simplex.is_some() == nasterov_simplex.is_some());
            }
            
            if asstert_dist{
                assert!((test_dist - nasterov_distance).abs() < 0.1);
            }  

            if print_iterations {
                println!("Orignial Simplex is Some {:?} Interations: {original_interations}", original_simplex.is_some());  
                println!("Nasterov Simplex is Some {:?} Interations: {nasterov_interations}", nasterov_simplex.is_some()); 
                original_iteration_sum += original_interations;
                nasterov_iteration_sum += nasterov_interations;
            }
                   
            i += 1;
        }

        if print_iterations {
            println!("Orignial Interations per Case: {:?}", (original_iteration_sum as f32) / json_data.as_array().unwrap().len() as f32); 
            println!("Nasterov Interations per Case: {:?}", (nasterov_iteration_sum as f32) / json_data.as_array().unwrap().len() as f32);
        }
    }
}
