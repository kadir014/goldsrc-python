"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

import pygame
import moderngl

from .container import Container


class Widget:
    """
    Base UI widget class.
    """

    # TODO: use custom vectors for position
    def __init__(self,
            container: Container,
            position: tuple[float, float],
            size: tuple[float, float],
            program_name: str = "ui"
            ):
        self.container = container
        self.container.widgets.append(self)

        self.position = position
        self.size = size

        # Pygame Surface
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA).convert_alpha()
        self.surface.fill((0, 0, 0, 0))

        # ModernGL Texture
        self.texture = self.container.engine.renderer.context.texture(
            self.surface.get_size(),
            4
        )
        
        self.texture.filter = (moderngl.NEAREST, moderngl.NEAREST)

        # Shader program
        self.program_name = program_name
        self.program = self.container.engine.renderer.get_shader(self.program_name)

        # VAO
        quad_vertices = self.container.engine.renderer.map_coords(
            *self.position, *self.size)
        quad_uvs = [0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0]
        quad_indices = [0, 1, 2, 1, 2, 3]

        self.vbo = self.container.engine.renderer.create_bo(quad_vertices)
        self.uvbo = self.container.engine.renderer.create_bo(quad_uvs)
        self.ibo = self.container.engine.renderer.create_bo(quad_indices)

        self.vao = self.container.engine.renderer.context.vertex_array(
            self.program,
            [
                (self.vbo,  "2f", "in_position"),
                (self.uvbo, "2f", "in_uv")
            ],
            self.ibo
        )

        self.enabled = True

    def update_texture(self):
        """ Update texture data. """
        self.texture.write(pygame.image.tostring(self.surface, "RGBA"))

    def update(self):
        """ Update widget. """
        NotImplemented

    def render(self):
        """ Render widget. """
        
        self.texture.use()

        with self.container.engine.renderer.no_depth_test():
            self.vao.render()

    def draw(self):
        """ Draw the widget display. """
        NotImplemented