import xml.etree.ElementTree as ET

import numpy as np
from pytransform3d.urdf import UrdfTransformManager

from distance3d.broad_phase import BoundingVolumeHierarchy

data_path = "../data/urdfs/tiago/"


def get_tiago_tm():
    urdf_file = "tiago.urdf"

    tm = UrdfTransformManager()
    f = open(data_path + urdf_file, "r")
    urdf = f.read()
    tm.load_urdf(urdf, package_dir=data_path, mesh_path=data_path)

    return tm


def get_tiago_bvh_from_tm(tm, base_frame2origin=np.eye(4)):
    bvh = BoundingVolumeHierarchy(tm, "base_footprint", base_frame2origin=base_frame2origin)
    bvh.fill_tree_with_colliders(tm, make_artists=True)

    return bvh


def tiago_limb(link):
    """Links of the same limb are not checked against each other: the hand (arm link 7 with the force-torque sensor,
    palm, fingers and safety box) and the base with the torso (base, wheels, casters, torso column and torso lift).
    Every other arm and head link is a limb on its own."""
    if link == "arm_7_link" or link.startswith(("hand_", "wrist_", "arm_tool")):
        return "hand"
    if link.startswith(("arm_", "head_")):
        return link
    return "base and torso"


def get_tiago_disabled_link_pairs():
    """Link pairs that are excluded from self-collision checks: links connected by fixed joints (one rigid body),
    rigid bodies connected by a joint (parent and child), links of the same limb (see tiago_limb), and the pairs in
    disable_collisions.srdf (PAL's blacklist and the pairs that MoveIt disables as adjacent or colliding in the default
    configuration).

    Returns a set of frozensets of two link names."""
    robot = ET.parse(data_path + "tiago.urdf").getroot()
    links = [link.get("name") for link in robot.findall("link")]
    joints = [(j.find("parent").get("link"), j.find("child").get("link"), j.get("type")) for j in robot.findall("joint")]

    # rigid bodies: links connected by fixed joints
    body = {link: link for link in links}
    def root(link):
        while body[link] != link:
            link = body[link]
        return link
    for parent, child, joint_type in joints:
        if joint_type == "fixed":
            body[root(child)] = root(parent)
    adjacent_bodies = {frozenset((root(parent), root(child))) for parent, child, joint_type in joints
                       if joint_type != "fixed"}

    disabled = set()
    for i, a in enumerate(links):
        for b in links[i:]:  # including colliders of the same link
            if (root(a) == root(b) or frozenset((root(a), root(b))) in adjacent_bodies
                    or tiago_limb(a) == tiago_limb(b)):
                disabled.add(frozenset((a, b)))
    for pair in ET.parse(data_path + "disable_collisions.srdf").getroot().findall("disable_collisions"):
        disabled.add(frozenset((pair.get("link1"), pair.get("link2"))))
    return disabled


def collider_link(collider_name):
    """Link of a collider named "collision:<link>/<index>" by the BVH."""
    return collider_name.split(":", 1)[1].rsplit("/", 1)[0]
