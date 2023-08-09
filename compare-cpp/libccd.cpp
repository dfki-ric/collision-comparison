#include "libccd.h"

#include <ccd/quat.h> // for work with quaternions

#include <glm/vec3.hpp> // glm::vec3
#include <glm/vec4.hpp> // glm::vec4
#include <glm/mat4x4.hpp> // glm::mat4
#include <glm/ext/matrix_transform.hpp> // glm::translate, glm::rotate, glm::scale
#include <glm/ext/matrix_clip_space.hpp> // glm::perspective
#include <glm/ext/scalar_constants.hpp> // glm::pi


namespace compare::libccd {

    glm::vec3 transform_point(glm::mat4x4 A2B, glm::vec3 point_in_A){
        return glm::vec3(A2B[3][1], A2B[3][2], A2B[3][3]) + glm::mat3x3(A2B) * point_in_A;
    }

    void sphere_support(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){

        Collider *collider = (Collider *)_collider;
        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);
        ccdVec3Normalize(&dir);

        float radius = Base::get_radius(*collider);
        ccd_vec3_t pos;
        ccdVec3Set(&pos, collider->colliderToOrigen[0][3], collider->colliderToOrigen[1][3], collider->colliderToOrigen[2][3]);

        ccdVec3Scale(&dir, radius);
        ccdVec3Add(&dir, &pos);
        ccdVec3Copy(_vec, &dir);
    }

    void cylider_support(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){

        Collider *collider = (Collider *)_collider;
        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);

        glm::vec3 local_dir = glm::transpose(glm::mat3x3(collider->colliderToOrigen)) * glm::vec3(dir.v[0], dir.v[1], dir.v[2]);
        float s = glm::sqrt(local_dir[0] * local_dir[0] + local_dir[1] * local_dir[1]);


        float z;
        if (local_dir[2] < 0.0){
            z = -0.5f * Base::get_height(*collider);
        } else {
            z = 0.5f * Base::get_height(*collider);
        }

        glm::vec3 local_vertex;
        if (s == 0.0) {
            local_vertex[0] = Base::get_radius(*collider);
            local_vertex[1] = 0;
            local_vertex[2] = z;
        } else {
            float d = Base::get_radius(*collider) / s;
            local_vertex[0] = local_dir[0] * d;
            local_vertex[1] = local_dir[1] * d;
            local_vertex[2] = z;
        }


        glm::vec3 result = transform_point(collider->colliderToOrigen, local_vertex);

        ccdVec3Set(_vec, result[0], result[1], result[2]);
    }

    void capsule_support(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){

        Collider *collider = (Collider *)_collider;
        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);

        glm::vec3 local_dir = glm::transpose(glm::mat3x3(collider->colliderToOrigen)) * glm::vec3(dir.v[0], dir.v[1], dir.v[2]);
        float s = glm::sqrt(local_dir[0] * local_dir[0] + local_dir[1] * local_dir[1] + local_dir[2] * local_dir[2]);

        glm::vec3 local_vertex;
        if (s == 0.0) {
            local_vertex[0] = Base::get_radius(*collider);
            local_vertex[1] = 0;
            local_vertex[2] = 0;
        }
        else {
            local_vertex = local_dir * (Base::get_radius(*collider) / s);
        }

        if (local_dir[2] > 0.0){
            local_vertex[2] += 0.5 * Base::get_height(*collider);
        }
        else{
            local_vertex[2] -= 0.5 * Base::get_height(*collider);
        }

        glm::vec3 result = transform_point(collider->colliderToOrigen, local_vertex);

        ccdVec3Set(_vec, result[0], result[1], result[2]);
    }

    void box_support(const void *_collider, const ccd_vec3_t *_dir, ccd_vec3_t *_vec){

        Collider *collider = (Collider *)_collider;
        ccd_vec3_t dir;
        ccdVec3Copy(&dir, _dir);

        glm::vec3 local_dir = glm::transpose(glm::mat3x3(collider->colliderToOrigen)) * glm::vec3(dir.v[0], dir.v[1], dir.v[2]);

        glm::vec3 local_vertex;
        local_vertex[0] = Base::get_size_x(*collider) * (0.5f * (local_dir[0] >= 0) + -0.5f * (local_dir[0] < 0));
        local_vertex[1] = Base::get_size_y(*collider) * (0.5f * (local_dir[1] >= 0) + -0.5f * (local_dir[1] < 0));
        local_vertex[2] = Base::get_size_z(*collider) * (0.5f * (local_dir[2] >= 0) + -0.5f * (local_dir[2] < 0));

        glm::vec3 result = transform_point(collider->colliderToOrigen, local_vertex);
        ccdVec3Set(_vec, result[0], result[1], result[2]);

    }

    ccd_support_fn get_support_function(Collider collider){
        if (collider.type == ColliderType::Sphere){
            return sphere_support;
        }

        if (collider.type == ColliderType::Cylinder){
            return cylider_support;
        }

        if (collider.type == ColliderType::Capsule){
            return capsule_support;
        }

        if (collider.type == ColliderType::Box){
            return box_support;
        }
    }

    void get_case(Collider collider0, Collider collider1, LibccdCase& libccd_case){
        CCD_INIT(&libccd_case.ccd);

        libccd_case.ccd.support1       = get_support_function(collider0);
        libccd_case.ccd.support2       = get_support_function(collider1);
        libccd_case.ccd.max_iterations = 100;

        libccd_case.collider0 = collider0;
        libccd_case.collider1 = collider1;
    }

    void get_cases(Case *base_cases, LibccdCase *libccd_cases, int length){
        for (int i = 0; i < length; i++) {
            get_case(base_cases[i].collider0, base_cases[i].collider1, libccd_cases[i]);
        }
    }

    bool get_intersection(LibccdCase& libccd_case) {
        int intersect = ccdGJKIntersect(&libccd_case.collider0, &libccd_case.collider1, &libccd_case.ccd);
        return intersect == 1;
    }
}