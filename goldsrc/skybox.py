"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import Union, TYPE_CHECKING

from pathlib import Path

import pygame

from .factory import create_cube_mesh
from .math import flatten_mat

if TYPE_CHECKING:
    from .engine import Engine
    from .camera import Camera


class Skybox:
    """
    Skybox class.
    """

    def __init__(self,
            engine: "Engine",
            texture_paths: dict[str, Union[Path, str]],
            flip_textures: bool = False
            ):
        self.engine = engine

        cube = create_cube_mesh(1.0)
        self.vertices = cube[0]
        self.normals = cube[1]
        self.uv_coords = cube[2]

        self.program = self.engine.renderer.get_shader("skybox")

        # Top =    +Y
        # Bottom = -Y
        # Left =   -X
        # Right =  +X
        # Front =  -Z
        # Back =   +Z

        textures = {
            "top": None,
            "bottom": None,
            "left": None,
            "right": None,
            "front": None,
            "back": None
        }

        for side in texture_paths:
            if side.lower() in ("top", "+y", "y+", "posy", "ypos"):
                textures["top"] = pygame.image.load(texture_paths[side])

            elif side.lower() in ("bottom", "-y", "y-", "negy", "yneg"):
                textures["bottom"] = pygame.image.load(texture_paths[side])

            elif side.lower() in ("left", "-x", "x-", "negx", "xneg"):
                textures["left"] = pygame.image.load(texture_paths[side])

            elif side.lower() in ("right", "+x", "x+", "posx", "xpos"):
                textures["right"] = pygame.image.load(texture_paths[side])

            elif side.lower() in ("front", "-z", "z-", "negz", "zneg"):
                textures["front"] = pygame.image.load(texture_paths[side])

            elif side.lower() in ("back", "+z", "z+", "posz", "zpos"):
                textures["back"] = pygame.image.load(texture_paths[side])

        combined = pygame.image.tostring(textures["right"], "RGB", flip_textures) +  \
                   pygame.image.tostring(textures["left"], "RGB", flip_textures) +   \
                   pygame.image.tostring(textures["top"], "RGB", flip_textures) +    \
                   pygame.image.tostring(textures["bottom"], "RGB", flip_textures) + \
                   pygame.image.tostring(textures["back"], "RGB", flip_textures) +   \
                   pygame.image.tostring(textures["front"], "RGB", flip_textures)
        
        size = textures["top"].get_width()

        self.cubemap = self.engine.renderer.context.texture_cube(
            (size, size),
            3,
            combined
        )

        self.create_vao()

    def create_vao(self):
        """ Create VAO (Vertex Array Object) """

        self.vbo = self.engine.renderer.create_bo(self.vertices)
        self.nbo = self.engine.renderer.create_bo(self.normals)
        self.uvbo = self.engine.renderer.create_bo(self.uv_coords)

        self.vao = self.engine.renderer.context.vertex_array(
            self.program,
            [
                (self.vbo,  "3f", "in_position"),
                (self.nbo,  "3f", "in_normal"),
                (self.uvbo, "2f", "in_uv")
            ]
        )

    def update(self, camera: "Camera"):
        """ Update matrix uniforms """

        # Projection and view matrices
        projection = camera.projection
        view = camera.get_view_matrix()

        # Hacky solution to keep skybox in place
        view[3][0] = 0
        view[3][1] = 0
        view[3][2] = 0

        self.program["u_projection"].value = flatten_mat(projection)
        self.program["u_view"].value = flatten_mat(view)

    def render(self):
        """ Render skybox VAO """
        self.cubemap.use()
        self.vao.render()