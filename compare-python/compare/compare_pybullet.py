import json

import numpy as np
import pybullet as pb
import pytransform3d.rotations as pr
from distance3d import benchmark
from src import get_nao_bvh, load_test_file

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

# Make sure the internal data structures are already initialized/ caches are  warmed up before starting the actual benchmark
# Use the last entry of the case file so that during the actual benchmark,
# PyBullet cannot reuse a potentially cached result for the first case:
last_collision_pair = collision_objects[-1]
dist = pb.getClosestPoints(last_collision_pair[0], last_collision_pair[1], np.inf, physicsClientId=pcid)[0][8]
dist = pb.getClosestPoints(last_collision_pair[0], last_collision_pair[1], np.inf, physicsClientId=pcid)[0][8]

timer = benchmark.Timer()
timer.start("pybullet")
#pb.performCollisionDetection(pcid)
for _ in range(10):
    for (c1, c2) in collision_objects:
            dist = pb.getClosestPoints(c1, c2, np.inf, physicsClientId=pcid)[0][8]
            #dist = len(pb.getContactPoints(c1, c2, physicsClientId=pcid)) > 0

result = {}

duration = timer.stop("pybullet")
micro = duration * 1000000
result["Pybullet"] = micro / 10.0
print(f"Pybullet: {micro}")

pb.disconnect(physicsClientId=pcid)

file = open(f"./pybullet_result.json", "w")
json.dump(result, file, indent=4)
