"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import Union

import os
import zipfile
import shutil
from pathlib import Path
from dataclasses import dataclass

from .math import flatten_2dlist


@dataclass
class ObjMesh:
    """
    Mesh with a material specified in the OBJ file.
    """

    material: str
    vertices: list[tuple[float, float, float]]
    normals: list[tuple[float, float, float]]
    uv_coords: list[tuple[float, float, float]]


class Obj:
    """
    Wavefront OBJ model.
    """

    def __init__(self,
            name: str,
            meshes: list[ObjMesh],
            smooth_shading: bool,
            material: str,
            ):
        self.name = name

        self.meshes = meshes

        self.smooth_shading = smooth_shading

        self.material = material


class ObjAnimation:
    """
    Sequence of Wavefront OBJ animation frames.
    """

    def __init__(self, frames: list[Obj]):
        self.frames = frames
        self.frame_count = len(self.frames)


def parse_raw(obj_content: str) -> Obj:
    """
    Parse Wavefront OBJ string.

    Doesn't support quad faces yet. If you are exporting from Blender, you
    have to turn "Triangulate faces" option on.

    @param obj_content String containing OBJ content
    @return Parsed OBJ model
    """

    name = ""
    material = ""

    vertices = []
    uv_coords = []
    normals = []

    # Mesh groups separated by material name
    groups = {}
    current_group = ""

    smooth_shading = False

    for line in obj_content.split("\n"):
        line = line.split()

        # Skip empty line
        if len(line) == 0: continue

        # Object name
        # o name
        elif line[0] == "o":
            name = line[1]

        # Object material
        # mtllib material
        elif line[0] == "mtllib":
            material = line[1]

        # Mesh material
        # usemtl material
        elif line[0] == "usemtl":
            current_group = line[1]
            groups[current_group] = {
                "vertex_indices": [],
                "normal_indices": [],
                "uv_indices": []
            }

        # Vertices
        # v x y z
        elif line[0] == "v":
            vertices.append([float(line[1]), float(line[2]), float(line[3])])

        # UV (texture) coordinates
        # vt x y
        elif line[0] == "vt":
            uv_coords.append([float(line[1]), float(line[2])])

        # Normals
        # vn x y z
        elif line[0] == "vn":
            normals.append([float(line[1]), float(line[2]), float(line[3])])

        # Face triangles
        # f triangle
        elif line[0] == "f":
            for d in line[1:]:
                h = d.split("/")
                groups[current_group]["vertex_indices"].append(int(h[0]) - 1)
                groups[current_group]["uv_indices"].append(int(h[1]) - 1)
                groups[current_group]["normal_indices"].append(int(h[2]) - 1)

        # Smooth shading
        # s 1/0  or  s on/off
        elif line[0] == "s":
            if line[1] in ("on", "1"):
                smooth_shading = True
            else:
                smooth_shading = False

    meshes = []

    # Create meshes from face and material info
    for group in groups:
        meshes.append(
            ObjMesh(
                group,
                flatten_2dlist([vertices[i] for i in groups[group]["vertex_indices"]]),
                flatten_2dlist([normals[i] for i in groups[group]["normal_indices"]]),
                flatten_2dlist([uv_coords[i] for i in groups[group]["uv_indices"]])
            )
        )

    return Obj(
        name,
        meshes,
        smooth_shading,
        material
    )


def parse(filepath: Union[Path, str]) -> Obj:
    """ 
    Parse Wavefront OBJ file.

    Doesn't support quad faces yet. If you are exporting from Blender, you
    have to turn "Triangulate faces" option on.

    @param filepath Path to the OBJ file
    @return Parsed OBJ model
    """

    with open(filepath, "r") as obj_file:
        content = obj_file.read()

    return parse_raw(content)
        

def parse_animation(filepath: Union[Path, str]) -> ObjAnimation:
    """
    Parse OBJ animation file.

    @param filepath Path to the animation file.
    @return Parsed ObjAnimation
    """

    os.mkdir("_temp")

    with zipfile.ZipFile(filepath, "r") as zip:
        zip.extractall("_temp")

    with open("_temp/_temp", "r") as obja_file:
        content = obja_file.read()

    frames = []
    for frame in content.split("# frame\n"):
        # Skip empty lines
        if len(frame.strip()) > 0:
            frames.append(parse_raw(frame))

    shutil.rmtree("_temp")

    return ObjAnimation(frames)


def pack_animation_sequence(
        dir: Union[Path, str],
        out_path: Union[Path, str],
        compression: int = zipfile.ZIP_DEFLATED
        ):
    """
    Pack and compress sequence of OBJ files into one file.

    @param dir Directory of OBJ files
    @param out Output file path
    @param compression Compression method
    """

    dir = Path(dir)

    # Combine all OBJ files
    with open("_temp", "a") as out:
        for *_, files in os.walk(dir):
            for name in files:
                if name.endswith(".obj"):
                    frame = int(name.replace(".obj", "").split("_")[-1])
                    
                    with open(dir / name, "r") as obj:
                        obj_content = obj.read()

                    out.write(f"# frame\n")
                    out.write(obj_content)

    # Compress the combined OBJ sequence
    with zipfile.ZipFile(out_path, "w", compression) as zip:
        zip.write("_temp")

    os.remove("_temp")