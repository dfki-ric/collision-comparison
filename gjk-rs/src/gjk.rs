use glam::{DVec3, dvec3};

use crate::colliders::Collider;

#[allow(dead_code)]
#[derive(Copy, Clone, Debug)]
struct Vertex {
    v: DVec3,
    s0: DVec3,
    s1: DVec3,
}


pub struct GJKNesterov
{
    alpha: f64,
    omega: f64,
    tolerance: f64,

    simplex: [Vertex; 4],
    simplex_len: usize,
    ray: DVec3,
    ray_len: f64,
    ray_dir: DVec3,

    support_point: Vertex,
}



impl GJKNesterov
{
    pub fn new(ray_guess: Option<DVec3>, tolerance: f64) -> Self {

        let simplex = [Vertex::default(), Vertex::default(), Vertex::default(), Vertex::default()];
        let mut ray = ray_guess.unwrap_or(dvec3(1.0, 0.0, 0.0));
        let mut ray_len = ray.length();

        if ray_len < tolerance {
            ray = dvec3(1.0, 0.0, 0.0);
            ray_len = 1.0;
        }

        let ray_dir = ray;
        let support_point = Vertex { v: ray, s0: ray, s1: ray };

        Self {
            alpha: 0.0,
            omega: 0.0,
            tolerance,
            simplex,
            simplex_len: 0,
            ray,
            ray_len,
            ray_dir,
            support_point,
        }
    }

    pub fn distance_nesterov_accelerated(&mut self, collider1: &Collider, collider2: &Collider, max_iterations: usize) -> (bool, f64, usize){
        let upper_bound = 1000000000.0;
    
        let mut use_nesterov_acceleration = true;
        let normalize_support_direction = false;
    
        let inflation = 0.0;
    
        let mut inside = false;
        let mut distance = 0.0;
        let mut interation = 0;
    
        for i in 0..max_iterations {
            interation = i;
            let k = i as f64;
    
            if self.ray_len < self.tolerance {
                distance = -inflation;
                inside = true;
                break;
            }
    
            if use_nesterov_acceleration {
                let momentum = (k + 1.0) / (k + 3.0);
                let y = momentum * self.ray + (1.0 - momentum) * self.support_point.v;
                self.ray_dir = momentum * self.ray_dir + (1.0 - momentum) * y;
    
                if normalize_support_direction {
                    self.ray_dir = self.ray_dir.normalize();
                }
            } else {
                self.ray_dir = self.ray;
            }
    
            let s0 = collider1.get_support_point(-self.ray_dir);
            let s1 = collider2.get_support_point(self.ray_dir);
            self.support_point = Vertex::new(s0, s1);
    
            self.simplex[self.simplex_len] = self.support_point;
            self.simplex_len += 1;
    
            self.omega = self.ray_dir.dot(self.support_point.v) / self.ray_dir.length();
            if self.omega > upper_bound {
                distance = self.omega - inflation;
                inside = false;
                break;
            }
    
            if use_nesterov_acceleration {
                let frank_wolfe_duality_gap = 2.0 * self.ray.dot(self.ray - self.support_point.v);
                if frank_wolfe_duality_gap - self.tolerance <= 0.0 {
                    use_nesterov_acceleration = false;
                    self.simplex_len -= 1;
                    continue;
                }
            }
    
            let cv_check_passed = self.check_convergence();
            if i > 0 && cv_check_passed {
                self.simplex_len -= 1;

                if use_nesterov_acceleration {
                    use_nesterov_acceleration = false;
                    continue;
                }
                distance = self.ray_len - inflation;
    
                if distance < self.tolerance {
                    inside = true
                }
                break;
            }
    
            match self.simplex_len {
                1 => {
                    self.ray = self.support_point.v;
                }
                2 => inside = self.project_line_origen(),
                3 => inside = self.project_triangle_origen(),
                4 => inside = self.project_tetra_to_origen(),
                _ => {}
            }
    
            if !inside {
                self.ray_len = self.ray.length();
            }
    
            if inside || self.ray_len == 0.0 {
                distance = -inflation;
                inside = true;
                break;
            }
        }
    
        return (inside, distance, interation);
    }
    
    fn check_convergence(&mut self) -> bool {
        self.alpha = self.alpha.max(self.omega);
    
        let diff = self.ray_len - self.alpha;
    
        return (diff - self.tolerance * self.ray_len) <= 0.0;
    }
    
    fn origen_to_point(&mut self, a_index: usize, a: DVec3) {
        self.ray = a;
        self.simplex[0] = self.simplex[a_index];
        self.simplex_len = 1;
    }
    
    fn origen_to_segment(
        &mut self,
        a_index: usize,
        b_index: usize,
        a: DVec3,
        b: DVec3,
        ab: DVec3,
        ab_dot_a0: f64,
    ) {
        self.ray = (ab.dot(b) * a + ab_dot_a0 * b) / ab.length_squared();
        self.simplex[0] = self.simplex[b_index];
        self.simplex[1] = self.simplex[a_index];
        self.simplex_len = 2;
    }
    
    fn origen_to_triangle(
        &mut self,
        a_index: usize,
        b_index: usize,
        c_index: usize,
        abc: DVec3,
        abc_dot_a0: f64,
    ) -> bool {
        if abc_dot_a0 == 0.0 {
            self.simplex[0] = self.simplex[c_index];
            self.simplex[1] = self.simplex[b_index];
            self.simplex[2] = self.simplex[a_index];
            self.simplex_len = 3;
    
            self.ray = DVec3::ZERO;
            return true;
        }
    
        if abc_dot_a0 > 0.0 {
            self.simplex[0] = self.simplex[c_index];
            self.simplex[1] = self.simplex[b_index];
        } else {
            self.simplex[0] = self.simplex[b_index];
            self.simplex[1] = self.simplex[c_index];
        }
    
        self.simplex[2] = self.simplex[a_index];
        self.simplex_len = 3;
    
        self.ray = -abc_dot_a0 / abc.length_squared() * abc;
        if abc == DVec3::ZERO {
            self.ray = abc;
        }
    
        return false;
    }
    
    fn project_line_origen(&mut self) -> bool {
        let a_index = 1;
        let b_index = 0;
    
        let a = self.simplex[a_index].v;
        let b = self.simplex[b_index].v;
    
        let ab = b - a;
        let d = ab.dot(-a);
    
        if d == 0.0 {
            /* Two extremely unlikely cases:
                - AB is orthogonal to A: should never happen because it means the support
                function did not do any progress and GJK should have stopped.
                - A == origin
            In any case, A is the closest to the origin */
            self.origen_to_point(a_index, a);
            return a == DVec3::ZERO;
        }
    
        if d < 0.0 {
            self.origen_to_point(a_index, a);
        } else {
            self.origen_to_segment(a_index, b_index, a, b, ab, d);
        }
    
        return false;
    }
    
    fn project_triangle_origen(&mut self) -> bool {
        let a_index = 2;
        let b_index = 1;
        let c_index = 0;
    
        let a = self.simplex[a_index].v;
        let b = self.simplex[b_index].v;
        let c = self.simplex[c_index].v;
    
        let ab = b - a;
        let ac = c - a;
        let abc = ab.cross(ac);
    
        let edge_ac2o = abc.cross(ac).dot(-a);
    
        let t_b = |data: &mut Self| {
            let towards_b = ab.dot(-a);
            if towards_b < 0.0 {
                data.origen_to_point(a_index, a);
            } else {
                data.origen_to_segment(a_index, b_index, a, b, ab, towards_b)
            }
        };
    
        if edge_ac2o >= 0.0 {
            let towards_c = ac.dot(-a);
            if towards_c >= 0.0 {
                self.origen_to_segment(a_index, c_index, a, c, ac, towards_c)
            } else {
                t_b(self);
            }
        } else {
            let edge_ab2o = ab.cross(abc).dot(-a);
            if edge_ab2o >= 0.0 {
                t_b(self);
            } else {
                return self.origen_to_triangle(a_index, b_index, c_index, abc, abc.dot(-a));
            }
        }
    
        return false;
    }
    
    fn project_tetra_to_origen(&mut self) -> bool {
        let a_index = 3;
        let b_index = 2;
        let c_index = 1;
        let d_index = 0;
    
        let a = self.simplex[a_index].v;
        let b = self.simplex[b_index].v;
        let c = self.simplex[c_index].v;
        let d = self.simplex[d_index].v;
    
        let aa = a.length_squared();
    
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
    
        let region_inside = |data: &mut Self| {
            data.ray = DVec3::ZERO;
            true
        };
    
        let region_abc = |data: &mut Self| {
            data.origen_to_triangle(
                a_index,
                b_index,
                c_index,
                (b - a).cross(c - a),
                -c.dot(a_cross_b),
            )
        };
    
        let region_acd = |data: &mut Self| {
            data.origen_to_triangle(
                a_index,
                c_index,
                d_index,
                (c - a).cross(d - a),
                -d.dot(a_cross_c),
            )
        };
    
        let region_adb = |data: &mut Self| {
            data.origen_to_triangle(
                a_index,
                d_index,
                b_index,
                (d - a).cross(b - a),
                d.dot(a_cross_b),
            )
        };
    
        let region_ab = |data: &mut Self| {
            data.origen_to_segment(a_index, b_index, a, b, b - a, -ba_aa)
        };
    
        let region_ac = |data: &mut Self| {
            data.origen_to_segment(a_index, c_index, a, c, c - a, -ca_aa)
        };
    
        let region_ad = |data: &mut Self| {
            data.origen_to_segment(a_index, d_index, a, d, d - a, -da_aa)
        };
    
        let region_a = |data: &mut Self| data.origen_to_point(a_index, a);
    
        if ba_aa <= 0.0 {
            if -d.dot(a_cross_b) <= 0.0 {
                if ba * da_ba + bd * ba_aa - bb * da_aa <= 0.0 {
                    if da_aa <= 0.0 {
                        if ba * ba_ca + bb * ca_aa - bc * ba_aa <= 0.0 {
                            region_abc(self);
                        } else {
                            region_ab(self);
                        }
                    } else {
                        if ba * ba_ca + bb * ca_aa - bc * ba_aa <= 0.0 {
                            if ca * ba_ca + cb * ca_aa - cc * ba_aa <= 0.0 {
                                if ca * ca_da + cc * da_aa - cd * ca_aa <= 0.0 {
                                    region_acd(self);
                                } else {
                                    region_ac(self);
                                }
                            } else {
                                region_abc(self);
                            }
                        } else {
                            region_ab(self);
                        }
                    }
                } else {
                    if da * da_ba + dd * ba_aa - db * da_aa <= 0.0 {
                        region_adb(self);
                    } else {
                        if ca * ca_da + cc * da_aa - cd * ca_aa <= 0.0 {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= 0.0 {
                                region_ad(self);
                            } else {
                                region_acd(self);
                            }
                        } else {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= 0.0 {
                                region_ad(self);
                            } else {
                                region_ac(self);
                            }
                        }
                    }
                }
            } else {
                if c.dot(a_cross_b) <= 0.0 {
                    if ba * ba_ca + bb * ca_aa - bc * ba_aa <= 0.0 {
                        if ca * ba_ca + cb * ca_aa - cc * ba_aa <= 0.0 {
                            if ca * ca_da + cc * da_aa - cd * ca_aa <= 0.0 {
                                region_acd(self);
                            } else {
                                region_ac(self);
                            }
                        } else {
                            region_abc(self);
                        }
                    } else {
                        region_ad(self);
                    }
                } else {
                    if d.dot(a_cross_c) <= 0.0 {
                        if ca * ca_da + cc * da_aa - cd * ca_aa <= 0.0 {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= 0.0 {
                                region_ad(self);
                            } else {
                                region_acd(self);
                            }
                        } else {
                            if ca_aa <= 0.0 {
                                region_ac(self);
                            } else {
                                region_ad(self);
                            }
                        }
                    } else {
                        return region_inside(self);
                    }
                }
            }
        } else {
            if ca_aa <= 0.0 {
                if d.dot(a_cross_c) <= 0.0 {
                    if da_aa <= 0.0 {
                        if ca * ca_da + cc * da_aa - cd * ca_aa <= 0.0 {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= 0.0 {
                                if da * da_ba + dd * ba_aa - db * da_aa <= 0.0 {
                                    region_adb(self);
                                } else {
                                    region_ad(self);
                                }
                            } else {
                                region_acd(self);
                            }
                        } else {
                            if ca * ba_ca + cb * ca_aa - cc * ba_aa <= 0.0 {
                                region_ac(self);
                            } else {
                                region_abc(self);
                            }
                        }
                    } else {
                        if ca * ba_ca + cb * ca_aa - cc * ba_aa <= 0.0 {
                            if ca * ca_da + cc * da_aa - cd * ca_aa <= 0.0 {
                                region_acd(self);
                            } else {
                                region_ac(self);
                            }
                        } else {
                            if c.dot(a_cross_b) <= 0.0 {
                                region_abc(self);
                            } else {
                                region_acd(self);
                            }
                        }
                    }
                } else {
                    if c.dot(a_cross_b) <= 0.0 {
                        if ca * ba_ca + cb * ca_aa - cc * ba_aa <= 0.0 {
                            region_ac(self);
                        } else {
                            region_abc(self);
                        }
                    } else {
                        if -d.dot(a_cross_b) <= 0.0 {
                            if da * da_ba + dd * ba_aa - db * da_aa <= 0.0 {
                                region_adb(self);
                            } else {
                                region_ad(self);
                            }
                        } else {
                            return region_inside(self);
                        }
                    }
                }
            } else {
                if da_aa <= 0.0 {
                    if -d.dot(a_cross_b) <= 0.0 {
                        if da * ca_da + dc * da_aa - dd * ca_aa <= 0.0 {
                            if da * da_ba + dd * ba_aa - db * da_aa <= 0.0 {
                                region_adb(self);
                            } else {
                                region_ad(self);
                            }
                        } else {
                            if d.dot(a_cross_c) <= 0.0 {
                                region_acd(self);
                            } else {
                                region_adb(self);
                            }
                        }
                    } else {
                        if d.dot(a_cross_c) <= 0.0 {
                            if da * ca_da + dc * da_aa - dd * ca_aa <= 0.0 {
                                region_ad(self);
                            } else {
                                region_acd(self);
                            }
                        } else {
                            return region_inside(self);
                        }
                    }
                } else {
                    region_a(self);
                }
            }
        }
    
        return false;
    }
}

impl Vertex {
    fn new(s0: DVec3, s1: DVec3) -> Self {
        Self { v: s0 - s1, s0, s1 }
    }
}

impl Default for Vertex {
    fn default() -> Self {
        Self::new(DVec3::ZERO, DVec3::ZERO)
    }
}