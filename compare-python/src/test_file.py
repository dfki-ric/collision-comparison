import json
import os
import sys
from pathlib import Path

import open3d as o3d
from numpy import ndarray

from scipy.spatial import ConvexHull

import distance3d.colliders
import numpy as np

from distance3d.colliders import Sphere, Box, Capsule, Cylinder, MeshGraph
from distance3d.epa import epa
from distance3d.gjk import gjk


def to_dict(collider, mesh_path: str):
    type = collider.__class__.__name__
    if type == "MeshGraph":
        type = "Mesh"

    data = {
        "type": type,
        "collider2origin": collider.collider2origin().tolist()
    }

    if type == "Sphere":
        data["radius"] = collider.radius
    if type == "Box":
        data["size"] = collider.size.tolist()
    if type == "Capsule" or type == "Cylinder":
        data["radius"] = collider.radius
        data["height"] = collider.length
    if type == "Mesh":
        collider: distance3d.colliders.MeshGraph
        data["mesh_path"] = mesh_path

    return data

def load_mesh_from_obj(file_path: Path) -> tuple[ndarray, ndarray]:
    """
    Loads a mesh from a OBJ file
    :param file_path: The path to the OBJ file
    :return: The list of vertices and the list of triangle faces (faces being represented as 3 vertex indices)
    """
    vertices = []
    faces = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                if line[0] == "v":
                    vertex = list(map(float, line[2:].strip().split()))
                    if len(vertex) != 3:
                        raise ValueError(f"Mesh vertex should have 3 elements, but found {len(vertex)}")
                    vertices.append(vertex)
                elif line[0] == "f":
                    face = list(map(lambda x: int(x)-1, line[2:].strip().split()))
                    if len(face) != 3:
                        raise ValueError(f"Mesh face should have 3 elements, but found {len(face)}")
                    faces.append(face)
    except ValueError as e:
        print(f"Error: Could not parse mesh from '{file_path}': {e}", file=sys.stderr)
        exit(1)
    return np.array(vertices), np.array(faces)


def from_dict(data, data_path: Path):
    if data["type"] == "Sphere":
        collider = Sphere(np.array(data["collider2origin"])[:3, 3], data["radius"])
    elif data["type"] == "Box":
        collider = Box(np.array(data["collider2origin"]), np.array(data["size"]))
    elif data["type"] == "Capsule":
        collider = Capsule(np.array(data["collider2origin"]), data["radius"], data["height"])
    elif data["type"] == "Cylinder":
        collider = Cylinder(np.array(data["collider2origin"]), data["radius"], data["height"])
    elif data["type"] == "Mesh":
        vertices, faces = load_mesh_from_obj(Path(data_path, data["mesh_path"]))
        collider = MeshGraph(np.array(data["collider2origin"]), vertices, faces)
    else:
        print("Error: Unknown collider type")
        exit(1)
    mesh_path = Path(data_path, data["mesh_path"]) if "mesh_path" in data else None
    return collider, mesh_path


def convert_to_convex_hull_collider(collider: MeshGraph) -> MeshGraph:
    vertices_orig = np.array(collider.vertices)
    hull = ConvexHull(vertices_orig)
    hull_vertices = vertices_orig[hull.vertices]

    # because the indices in hull.simplices are pointing to entries in the original vertex-list,
    # we cannot use them easily to instantiate the new MeshGraph.
    # As a quick hack, just calculate a second convex hull and assume
    # that the input and output vertex-lists now stay the same. This way, the indices in final_hull.simplices
    # point perfectly into hull_vertices
    final_hull = ConvexHull(hull_vertices)
    assert len(final_hull.vertices) == len(hull_vertices)

    return MeshGraph(collider.mesh2origin, hull_vertices, final_hull.simplices)


def clean_collider_name(raw_name: str) -> str:
    # raw_name is assumed to have following form: "[collision|visual]:actual_name/suffix"
    parts = raw_name.split(':')
    if len(parts) != 2 or parts[0] not in ["collision", "visual"]:
        raise Exception(f"Collider name did not have expected form: {raw_name}")

    return parts[1][:parts[1].rfind("/")]


def write_mesh_file(collider: MeshGraph, file_name: str, save_path: str):
    path = Path(save_path, file_name+".obj")
    if os.path.exists(path): return
    with open(path, "w") as f:
        for vertex in collider.vertices:
            f.write("v {} {} {}\n".format(vertex[0], vertex[1], vertex[2]))
        for triangle in collider.triangles:
            # indices in the .obj file format start at 1, therefore increment all indices first:
            f.write("f {} {} {}\n".format(triangle[0]+1, triangle[1]+1, triangle[2]+1))


def simplify_mesh(collider: MeshGraph, max_num_points):
    # Use Euler's formula to approximately convert from max. number of points to the corresponding number of faces.
    # If the mesh is already simple enough, use the existing number of faces as target value
    max_num_faces = min(max(4, 2 * max_num_points - 4), len(collider.triangles))

    # Convert collider into open3d mesh
    mesh = o3d.geometry.TriangleMesh()
    mesh.vertices = o3d.utility.Vector3dVector(collider.vertices)
    mesh.triangles = o3d.utility.Vector3iVector(collider.triangles)
    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()

    simplified: o3d.cuda.pybind.geometry.TriangleMesh = mesh.simplify_quadric_decimation(
        target_number_of_triangles=max_num_faces
    )
    simplified.remove_duplicated_vertices()
    simplified.remove_unreferenced_vertices()

    if len(simplified.triangles) > max_num_faces:
        print(f"Warning: Failed to simplify mesh. Should have {max_num_faces}, but still has {len(simplified.triangles)} faces")

    return MeshGraph(collider.mesh2origin, np.asarray(simplified.vertices), np.asarray(simplified.triangles))


def signed_distance(collider0, collider1):
    """
    Computes the signed distance between the colliders. For negative distances, this uses EPA.
    """
    dist, _, _, simplex = gjk(collider0, collider1)

    if dist > 0:
        return dist

    try:
        mtv, _, success = epa(simplex, collider0, collider1)
        if success:
            depth = np.linalg.norm(mtv)
            if depth > 0:
                return -depth
    except Exception:
        pass

    return 0.0


def write_test_file(cases, save_path: str, file_name: str,
                    hull_max_vertices: int | None = None,
                    clean_collider_names = True,
                    omit_reference_distance = False,
                    compute_convex_hulls = True
                    ):
    """
    :param cases: The benchmark cases to save.
    :param save_path: The directory to save the test cases into.
    :param file_name: The file name of the current case file.
    :param hull_max_vertices: When using convex hull colliders,
    sets a maximum number of vertices to simplify the hull down to.
    :param clean_collider_names: Whether to clean the collider names,
    intended to be used if the collider names are taken from a URDF and still have some pre-/suffixes.
    :param omit_reference_distance: Whether to include a reference distance in the JSON file.
    Useful when handling very large meshes for which the distance would take a long time to compute.
    :param compute_convex_hulls: Whether the convex hulls should be computed.
    Set this to false if the meshes are already convex.
    """
    shapes = []
    subdirectory_name = save_path.split("/")[-1]
    i = 0
    for case in cases:
        print("Case: ", i)

        collider0 = case[0][1]
        collider1 = case[1][1]
        if clean_collider_names:
            collider0_name = clean_collider_name(case[0][0])
            collider1_name = clean_collider_name(case[1][0])
        else:
            collider0_name = case[0][0]
            collider1_name = case[1][0]

        if type(collider0) == MeshGraph:
            if compute_convex_hulls:
                collider0 = convert_to_convex_hull_collider(collider0)
            if hull_max_vertices is not None:
                collider0 = simplify_mesh(collider0, hull_max_vertices)
            write_mesh_file(collider0, collider0_name, save_path + "/meshes")

        if type(collider1) == MeshGraph:
            if compute_convex_hulls:
                collider1 = convert_to_convex_hull_collider(collider1)
            if hull_max_vertices is not None:
                collider1 = simplify_mesh(collider1, hull_max_vertices)
            write_mesh_file(collider1, collider1_name, save_path + "/meshes")

        if omit_reference_distance:
            distance = -999
        else:
            distance, _, _, _ = gjk(collider0, collider1)
        data = {
            "case": i,
            "collider1": to_dict(collider0, subdirectory_name + "/meshes/" + collider0_name + ".obj"),
            "collider2": to_dict(collider1, subdirectory_name + "/meshes/" + collider1_name + ".obj"),
            "distance": distance,
            "signed_distance": signed_distance(collider0, collider1),
        }
        shapes.append(data)
        i += 1

    file = open(f"{save_path}/{file_name}", "w")
    json.dump(shapes, file, indent=4)


def load_test_file(path: str):
    file = open(path)
    data_path = Path(path[:path.rfind("/")])
    data = json.load(file)

    colliders = []
    for case in data:
        colliders.append([from_dict(case["collider1"], data_path), from_dict(case["collider2"], data_path)])

    return colliders
