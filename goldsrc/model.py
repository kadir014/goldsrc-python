"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import Optional, Union, TYPE_CHECKING

from pathlib import Path
from time import time

import pygame
import moderngl
import glm

from .math import flatten_mat
from .factory import create_plane_mesh, create_cube_mesh
from .objparser import parse, parse_animation, ObjAnimation, ObjMesh

if TYPE_CHECKING:
    from .engine import Engine
    from .camera import Camera
    from .light import BasicLight


class Model:
    """
    Base 3D model class.

    color argument is only used when flat or unlitflat shaders are used.
    """

    def __init__(self,
            engine: "Engine",
            meshes: list[ObjMesh],
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            program_name: Optional[str] = "base",
            wireframe: bool = False
            ):
        self.engine = engine

        self.program_name = program_name
        self.program = self.engine.renderer.get_shader(self.program_name)

        self.meshes = meshes
        self.color = color
        self.wireframe = wireframe

        # Internal ModernGL objects
        self.vbo: moderngl.Buffer = None
        self.nbo: moderngl.Buffer = None
        self.uvbo: moderngl.Buffer = None
        self.vao: moderngl.VertexArray = None

    @property
    def color(self):
        return self.__color
    
    @color.setter
    def color(self, new_value: Union[tuple[float, float, float], glm.vec4]):
        self.__color = new_value

        if self.program_name in ("flat", "unlitflat"):
            self.program["u_color"] = self.__color

    def create_vao(self):
        """ Create VAO. """
        raise NotImplementedError

    def update(self,
            model: glm.mat4,
            projection: glm.mat4,
            view: glm.mat4,
            camera: "Camera",
            light: "BasicLight"
        ):
        """ Update shader uniforms. """

        # Vertex shader uniforms
        self.program["u_model"].value = flatten_mat(model)
        self.program["u_projection"].value = flatten_mat(projection)
        self.program["u_view"].value = flatten_mat(view)

        # Fragment shader uniforms
        if self.program_name in ("base", "flat", "normal"):
            self.program["u_view_position"] = camera.position.to_tuple()
            self.program["u_light_position"] = light.position.to_tuple()

            self.program["u_light_color"].value = light.color.to_tuple()
            self.program["u_ambient_intensity"].value = light.ambient_intensity
            self.program["u_diffuse_intensity"].value = light.diffuse_intensity
            self.program["u_specular_intensity"].value = light.specular_intensity
            self.program["u_specular_power"].value = light.specular_power
    
    def render(self):
        """ Render model. """
        raise NotImplementedError


class BasicModel(Model):
    """
    Basic 3D model with only one material and texture.

    Consider using helper constructors instead of creating it manually.
    """

    def __init__(self,
            engine: "Engine",
            meshes: list[ObjMesh],
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            texture_path: Optional[Union[Path, str]] = None,
            texture_repeat: bool = False,
            build_mipmaps: bool = True,
            program_name: Optional[str] = "base",
            wireframe: bool = False
            ):
        super().__init__(
            engine,
            meshes,
            color=color,
            program_name=program_name,
            wireframe=wireframe
        )

        # Basic model has only one mesh
        self.mesh = self.meshes[0]

        if texture_path is None: self.texture = None
        else: self.create_texture(texture_path, texture_repeat, build_mipmaps)

        self.create_vao()

    def create_texture(self,
            filepath: Union[Path, str],
            repeat: bool = False,
            build_mipmaps: bool = False
            ):
        """ Load and create texture. """

        surface = pygame.image.load(filepath)
        format = "RGB" # TODO: Detect format

        self.texture = self.engine.renderer.context.texture(
            surface.get_size(),
            len(format),
            pygame.image.tostring(surface, format, True)
        )

        self.texture.repeat_x = repeat
        self.texture.repeat_y = repeat

        if build_mipmaps: self.texture.build_mipmaps()

    def create_vao(self):
        """ Create VAO. """

        self.vbo = self.engine.renderer.create_bo(self.mesh.vertices)
        self.nbo = self.engine.renderer.create_bo(self.mesh.normals)
        self.uvbo = self.engine.renderer.create_bo(self.mesh.uv_coords)

        self.vao = self.engine.renderer.context.vertex_array(
            self.program,
            [
                (self.vbo,  "3f", "in_position"),
                (self.nbo,  "3f", "in_normal"),
                (self.uvbo, "2f", "in_uv")
            ]
        )

    def render(self):
        """ Render model. """

        if self.texture is not None: self.texture.use(0)

        if self.wireframe: self.vao.render(moderngl.LINES)
        else: self.vao.render()

    @classmethod
    def from_obj(cls,
            engine: "Engine",
            obj_path: Union[Path, str],
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            texture_path: Optional[Union[Path, str]] = None,
            texture_repeat: bool = False,
            build_mipmaps: bool = True,
            program_name: Optional[str] = "base",
            wireframe: bool = False
            ):
        """ Create model from OBJ file. """
        
        obj = parse(obj_path)

        return cls(
            engine,
            obj.meshes,
            color=color,
            texture_path=texture_path,
            texture_repeat=texture_repeat,
            build_mipmaps=build_mipmaps,
            program_name=program_name,
            wireframe=wireframe
        )

    @classmethod
    def from_plane(cls,
            engine: "Engine",
            size: float,
            scale_uv_coords: bool = False,
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            texture_path: Optional[Union[Path, str]] = None,
            texture_repeat: bool = False,
            build_mipmaps: bool = True,
            program_name: Optional[str] = "base",
            wireframe: bool = False
            ):
        """ Create model from plane geometry. """
        
        vertices, normals, uv_coords = create_plane_mesh(size, scale_uv_coords)

        mesh = ObjMesh("", vertices, normals, uv_coords)

        return cls(
            engine,
            [mesh],
            color=color,
            texture_path=texture_path,
            texture_repeat=texture_repeat,
            build_mipmaps=build_mipmaps,
            program_name=program_name,
            wireframe=wireframe
        )
    
    @classmethod
    def from_cube(cls,
            engine: "Engine",
            size: float,
            scale_uv_coords: bool = False,
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            texture_path: Optional[Union[Path, str]] = None,
            texture_repeat: bool = False,
            build_mipmaps: bool = True,
            program_name: Optional[str] = "base",
            wireframe: bool = False
            ):
        """ Create model from cube geometry. """
        
        vertices, normals, uv_coords = create_cube_mesh(size, scale_uv_coords)

        mesh = ObjMesh("", vertices, normals, uv_coords)

        return cls(
            engine,
            [mesh],
            color=color,
            texture_path=texture_path,
            texture_repeat=texture_repeat,
            build_mipmaps=build_mipmaps,
            program_name=program_name,
            wireframe=wireframe
        )
    

class MultiMaterialModel(Model):
    """
    Model with multiple meshes with different materials.

    Consider using helper constructors instead of creating it manually.
    """

    def __init__(self,
            engine: "Engine",
            meshes: list[ObjMesh],
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            program_name: Optional[str] = "base",
            texture_repeat: bool = False,
            build_mipmaps: bool = True,
            wireframe: bool = False
            ):
        super().__init__(engine, meshes, color, program_name, wireframe)

        self.create_textures(texture_repeat, build_mipmaps)

        self.create_vao()

    def create_textures(self, repeat: bool = False, build_mipmaps: bool = True):
        """ Load and create textures. """

        self.textures = []

        for mesh in self.meshes:
            surface = pygame.image.load(f"assets/textures/headcrab/{mesh.material}")
            # TODO: Detect format
            format = "RGB"

            texture = self.engine.renderer.context.texture(
                surface.get_size(),
                len(format),
                pygame.image.tostring(surface, format, True)
            )

            texture.repeat_x = repeat
            texture.repeat_y = repeat

            if build_mipmaps: texture.build_mipmaps()

            self.textures.append(texture)

    def create_vao(self):
        """ Create VAO. """

        # Merge all meshes info into single array
        vertices = []
        normals = []
        uv_coords = []
        for mesh in self.meshes: vertices += mesh.vertices
        for mesh in self.meshes: normals += mesh.normals
        for mesh in self.meshes: uv_coords += mesh.uv_coords

        self.vbo = self.engine.renderer.create_bo(vertices)
        self.nbo = self.engine.renderer.create_bo(normals)
        self.uvbo = self.engine.renderer.create_bo(uv_coords)

        self.vao = self.engine.renderer.context.vertex_array(
            self.program,
            [
                (self.vbo,  "3f", "in_position"),
                (self.nbo,  "3f", "in_normal"),
                (self.uvbo, "2f", "in_uv")
            ]
        )

    def render(self):
        """ Render model. """

        for i, mesh in enumerate(self.meshes):
            self.textures[i].use(0)

            # Get the starting index for render
            start = 0
            for j in range(i):
                start += len(self.meshes[j].vertices) // 3

            # Get the number of vertices to render
            verts = len(mesh.vertices) // 3

            if self.wireframe: self.vao.render(moderngl.LINES, vertices=verts, first=start)
            else: self.vao.render(vertices=verts, first=start)


class BasicAnimatedModel(Model):
    """
    Basic animated 3D model with only one material and texture.

    Consider using helper constructors instead of creating it manually.
    """

    def __init__(self,
            engine: "Engine",
            meshes: list[ObjMesh],
            obj_animation: ObjAnimation,
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            texture_path: Optional[Union[Path, str]] = None,
            texture_repeat: bool = False,
            build_mipmaps: bool = True,
            program_name: Optional[str] = "base",
            wireframe: bool = False
            ):
        super().__init__(
            engine,
            meshes,
            color=color,
            program_name=program_name,
            wireframe=wireframe
        )

        self.obj_animation = obj_animation
        self.frame = 0
        self.frame_count = self.obj_animation.frame_count
        self.frames = self.obj_animation.frames
        self.is_playing = False
        self.loop = False

        if texture_path is None: self.texture = None
        else: self.create_texture(texture_path, texture_repeat, build_mipmaps)

        self.create_vao()

    def play(self, loop: bool = False):
        self.frame = 0
        self.is_playing = True
        self.loop = loop

    def stop(self):
        self.is_playing = False

    def pause(self):
        self.is_playing = False

    def unpause(self):
        self.is_playing = True

    def create_texture(self,
            filepath: Union[Path, str],
            repeat: bool = False,
            build_mipmaps: bool = False
            ):
        """ Load and create texture. """

        surface = pygame.image.load(filepath)
        format = "RGB" # TODO: Detect format

        self.texture = self.engine.renderer.context.texture(
            surface.get_size(),
            len(format),
            pygame.image.tostring(surface, format, True)
        )

        self.texture.repeat_x = repeat
        self.texture.repeat_y = repeat

        if build_mipmaps: self.texture.build_mipmaps()

    def create_vao(self):
        """ Create VAO. """

        mesh = self.frames[0].meshes[0]

        self.vbo = self.engine.renderer.create_bo(mesh.vertices)
        self.nbo = self.engine.renderer.create_bo(mesh.normals)
        self.uvbo = self.engine.renderer.create_bo(mesh.uv_coords)

        self.vao = self.engine.renderer.context.vertex_array(
            self.program,
            [
                (self.vbo,  "3f", "in_position"),
                (self.nbo,  "3f", "in_normal"),
                (self.uvbo, "2f", "in_uv")
            ]
        )

    def update(self,
            model: glm.mat4,
            projection: glm.mat4,
            view: glm.mat4,
            camera: "Camera",
            light: "BasicLight"
        ):
        """ Update model. """
        super().update(model, projection, view, camera, light)

        if self.is_playing:
            self.frame += 1
            if self.frame == self.frame_count:
                if self.loop: self.frame = 0
                else: self.frame = self.frame_count - 1

            current_obj = self.frames[self.frame]
            # Basic model doesn't have multiple meshes
            mesh = current_obj.meshes[0]

            self.vbo.write(self.engine.renderer.to_buffer(mesh.vertices))
            self.nbo.write(self.engine.renderer.to_buffer(mesh.normals))
            # UV coordinates will not probably change during animation but
            # update them as well regardless
            self.uvbo.write(self.engine.renderer.to_buffer(mesh.uv_coords))

    def render(self):
        """ Render model. """

        if self.texture is not None: self.texture.use(0)

        if self.wireframe: self.vao.render(moderngl.LINES)
        else: self.vao.render()

    @classmethod
    def from_obja(cls,
            engine: "Engine",
            obja_path: Union[Path, str],
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            texture_path: Optional[Union[Path, str]] = None,
            texture_repeat: bool = False,
            build_mipmaps: bool = True,
            program_name: Optional[str] = "base",
            wireframe: bool = False
            ):
        """ Create animated model from OBJA file. """
        
        obj_animation = parse_animation(obja_path)

        return cls(
            engine,
            None,
            obj_animation,
            color=color,
            texture_path=texture_path,
            texture_repeat=texture_repeat,
            build_mipmaps=build_mipmaps,
            program_name=program_name,
            wireframe=wireframe
        )
    

class MultiMaterialAnimatedModel(Model):
    """
    Animated model with multiple meshes with different materials.

    Consider using helper constructors instead of creating it manually.
    """

    def __init__(self,
            engine: "Engine",
            meshes: list[ObjMesh],
            obj_animation: ObjAnimation,
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            texture_repeat: bool = False,
            build_mipmaps: bool = True,
            program_name: Optional[str] = "base",
            wireframe: bool = False
            ):
        super().__init__(
            engine,
            meshes,
            color=color,
            program_name=program_name,
            wireframe=wireframe
        )

        self.obj_animation = obj_animation
        self.frame = 0
        self.duration = 41
        self.last_frame = time()
        self.frame_count = self.obj_animation.frame_count
        self.frames = self.obj_animation.frames
        self.default_frame = self.frames[0]
        self.is_playing = False
        self.loop = False

        self.create_textures(texture_repeat, build_mipmaps)

        self.create_vao()

    def play(self, loop: bool = False):
        self.frame = 0
        self.is_playing = True
        self.loop = loop

    def stop(self):
        self.is_playing = False

    def pause(self):
        self.is_playing = False

    def unpause(self):
        self.is_playing = True

    def create_textures(self, repeat: bool = False, build_mipmaps: bool = True):
        """ Load and create textures. """

        self.textures = []

        for mesh in self.frames[0].meshes:
            surface = pygame.image.load(f"assets/textures/headcrab/{mesh.material}")
            format = "RGB" # TODO: Detect format

            texture = self.engine.renderer.context.texture(
                surface.get_size(),
                len(format),
                pygame.image.tostring(surface, format, True)
            )

            texture.repeat_x = repeat
            texture.repeat_y = repeat

            if build_mipmaps: texture.build_mipmaps()

            self.textures.append(texture)

    def create_vao(self):
        """ Create VAO. """

        # Merge all meshes info into single array
        vertices = []
        normals = []
        uv_coords = []
        for mesh in self.default_frame.meshes: vertices += mesh.vertices
        for mesh in self.default_frame.meshes: normals += mesh.normals
        for mesh in self.default_frame.meshes: uv_coords += mesh.uv_coords

        self.vbo = self.engine.renderer.create_bo(vertices)
        self.nbo = self.engine.renderer.create_bo(normals)
        self.uvbo = self.engine.renderer.create_bo(uv_coords)

        self.vao = self.engine.renderer.context.vertex_array(
            self.program,
            [
                (self.vbo,  "3f", "in_position"),
                (self.nbo,  "3f", "in_normal"),
                (self.uvbo, "2f", "in_uv")
            ]
        )

    def update(self,
            model: glm.mat4,
            projection: glm.mat4,
            view: glm.mat4,
            camera: "Camera",
            light: "BasicLight"
        ):
        """ Update model. """
        super().update(model, projection, view, camera, light)

        now = time()
        if self.is_playing and now - self.last_frame > self.duration / 1000:
            self.last_frame = now

            self.frame += 1
            if self.frame == self.frame_count:
                if self.loop: self.frame = 0
                else: self.frame = self.frame_count - 1

            current_obj = self.frames[self.frame]
            # Merge all meshes info into single array
            vertices = []
            normals = []
            uv_coords = []
            for mesh in current_obj.meshes: vertices += mesh.vertices
            for mesh in current_obj.meshes: normals += mesh.normals
            #for mesh in current_obj.meshes: uv_coords += mesh.uv_coords

            self.vbo.write(self.engine.renderer.to_buffer(vertices))
            self.nbo.write(self.engine.renderer.to_buffer(normals))
            #self.uvbo.write(self.engine.renderer.to_buffer(uv_coords))

    def render(self):
        """ Render model. """

        for i, mesh in enumerate(self.frames[self.frame].meshes):
            self.textures[i].use(0)

            # Get the starting index for render
            start = 0
            for j in range(i):
                start += len(self.frames[self.frame].meshes[j].vertices) // 3

            # Get the number of vertices to render
            verts = len(mesh.vertices) // 3

            if self.wireframe: self.vao.render(moderngl.LINES, vertices=verts, first=start)
            else: self.vao.render(vertices=verts, first=start)

    @classmethod
    def from_obja(cls,
            engine: "Engine",
            obja_path: Union[Path, str],
            color: Union[tuple[float, float, float], glm.vec4] = (1.0, 1.0, 1.0, 1.0),
            texture_repeat: bool = False,
            build_mipmaps: bool = True,
            program_name: Optional[str] = "base",
            wireframe: bool = False
            ):
        """ Create animated model from OBJA file. """
        
        obj_animation = parse_animation(obja_path)

        return cls(
            engine,
            None,
            obj_animation,
            color=color,
            texture_repeat=texture_repeat,
            build_mipmaps=build_mipmaps,
            program_name=program_name,
            wireframe=wireframe
        )