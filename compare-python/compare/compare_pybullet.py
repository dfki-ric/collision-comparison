import json
import timeit

import numpy as np
import pybullet as pb
import pytransform3d.rotations as pr
from src import load_test_file

COLLISION_SHAPES = [
    "cylinder", "box", "capsule", "sphere"
]


def _pybullet_pos_orn(A2B):
    pos = A2B[:3, 3]
    orn = pr.quaternion_xyzw_from_wxyz(
        pr.quaternion_from_matrix(A2B[:3, :3]))
    return pos, orn


def get_multibody(shape, mesh_path, pcid):
    if type(shape).__name__ == "Cylinder":
        pos, orn = _pybullet_pos_orn(shape.cylinder2origin)
        collision = pb.createCollisionShape(
            shapeType=pb.GEOM_CYLINDER, radius=shape.radius, height=shape.length,
            physicsClientId=pcid)
    elif type(shape).__name__ == "Capsule":
        pos, orn = _pybullet_pos_orn(shape.capsule2origin)
        collision = pb.createCollisionShape(
            shapeType=pb.GEOM_CAPSULE, radius=shape.radius, height=shape.height,
            physicsClientId=pcid)
    elif type(shape).__name__ == "Sphere":
        pos, orn = shape.center(), np.array([0.0, 0.0, 0.0, 1.0])
        collision = pb.createCollisionShape(
            shapeType=pb.GEOM_SPHERE, radius=shape.radius,
            physicsClientId=pcid)
    elif type(shape).__name__ == "Box":
        pos, orn = _pybullet_pos_orn(shape.box2origin)
        collision = pb.createCollisionShape(
            shapeType=pb.GEOM_BOX, halfExtents=0.5 * shape.size,
            physicsClientId=pcid)
    elif type(shape).__name__ == "MeshGraph":
        pos, orn = _pybullet_pos_orn(shape.mesh2origin)
        collision = pb.createCollisionShape(
            shapeType=pb.GEOM_MESH,
            fileName = str(mesh_path),
            physicsClientId=pcid
        )
    else:
        print("Error: Unknown collider type")
        exit(1)

    multibody = pb.createMultiBody(
        baseMass=1, baseInertialFramePosition=[0, 0, 0],
        baseCollisionShapeIndex=collision, physicsClientId=pcid)
    pb.resetBasePositionAndOrientation(
        multibody, pos, orn, physicsClientId=pcid)

    return multibody


pcid = pb.connect(pb.DIRECT)
collision_objects = []

cases = load_test_file("../data/current.json")
for (collider1, mesh_path_1), (collider2, mesh_path_2) in cases:

    multibody1 = get_multibody(collider1, mesh_path_1, pcid)
    multibody2 = get_multibody(collider2, mesh_path_2, pcid)

    collision_objects.append((multibody1, multibody2))

def benchmark_pybullet():
    #pb.performCollisionDetection(pcid)
    for (c1, c2) in collision_objects:
            dist = pb.getClosestPoints(c1, c2, np.inf, physicsClientId=pcid)[0][8]
            #dist = len(pb.getContactPoints(c1, c2, physicsClientId=pcid)) > 0

# warm-up: 10 runs over all cases, as for the other implementations
# (initializes PyBullet's internal data structures and caches before the actual benchmark)
for _ in range(10):
    benchmark_pybullet()

result = {}

# same as for distance3d: median of 10 repetitions
times = timeit.repeat(benchmark_pybullet, repeat=10, number=1)
micro = np.median(times) * 1000000
result["Pybullet"] = micro
print(f"Pybullet: {micro:.2f}")

pb.disconnect(physicsClientId=pcid)

file = open(f"./pybullet_result.json", "w")
json.dump(result, file, indent=4)
