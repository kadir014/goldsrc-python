"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import TYPE_CHECKING

import sys
import struct
import platform
from contextlib import contextmanager

import pygame
import moderngl

from .path import source_path
from .ui import Container, Widget

if TYPE_CHECKING:
    from .engine import Engine


class Renderer:
    """
    Renderer.
    """

    def __init__(self, engine: "Engine"):
        self.engine = engine

        # Cached shader programs
        self.__programs = {}

        # Temporary context is used to get the multi-sampling limit
        tempcontext = moderngl.create_standalone_context()
        self.max_samples = tempcontext.max_samples
        tempcontext.release()

        # Multisampling of 32 makes colrs washed-out?? Keep it under 16
        if self.max_samples > 16: self.max_samples = 16

        # Initialize all Pygame modules
        pygame.init()

        # Set Pygame multisampling flags
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES,
                                        self.max_samples)

        # ! FORCE TESTING RESOLUTION
        self.engine.window_width, self.engine.window_height = (1280, 720)

        # Create window
        pygame.display.set_mode(
            (self.engine.window_width, self.engine.window_height),
            pygame.OPENGL | pygame.DOUBLEBUF
        )

        # Create ModernGL context
        self.context = moderngl.create_context()
        self.context.enable(moderngl.BLEND | moderngl.DEPTH_TEST)
        self.context.multisample = True

        # Game framebuffer
        # It doesn't have multisampling for post-process effects
        game_fbo_color = self.context.texture(
            (self.engine.window_width, self.engine.window_height),
            4
        )
        game_fbo_depth = self.context.depth_texture(
            (self.engine.window_width, self.engine.window_height)
        )
        self.game_fbo = self.context.framebuffer(
            color_attachments=game_fbo_color,
            depth_attachment=game_fbo_depth
        )

        self.clear_color = self.normalize_color((255, 255, 255))

        self.ui = Container(self.engine)

    @staticmethod
    def normalize_color(
            color: tuple[int, int, int]
            ) -> tuple[float, float, float]:
        """ Map RGB color from range [0, 255] to [0, 1]. """
        return (color[0] / 255, color[1] / 255, color[2] / 255)
    
    def map_coords(self,
            x: float,
            y: float,
            width: float,
            height: float
            ) -> tuple[float]:
        """
        Map 2D window coordinates into vertex coordinates.

        OpenGL's Coordinate System

         -1, 1           0, 1           1, 1
               ┌──────────────────────┐
               │                      │
         -1, 0 │         0, 0         │ 1, 0
               │                      │
               └──────────────────────┘
         -1, -1          0, -1          1, -1

        Pygame's Coordinate System

          0, 0          W/2, 0          W, 0
               ┌──────────────────────┐
               │                      │
        0, H/2 │       W/2, H/2       │ W, H/2
               │                      │
               └──────────────────────┘
          0, H          W/2, H          W, H
        """

        y = self.engine.window_height - y

        bottomleft = (x, y - height)
        bottomright = (x + width, y - height)
        topleft = (x, y)
        topright = (x + width, y)

        bottomleft = (bottomleft[0] / (self.engine.window_width / 2) - 1,
                      bottomleft[1] / (self.engine.window_height / 2) - 1)

        bottomright = (bottomright[0] / (self.engine.window_width / 2) - 1,
                       bottomright[1] / (self.engine.window_height / 2) - 1)

        topleft = (topleft[0] / (self.engine.window_width / 2) - 1,
                   topleft[1] / (self.engine.window_height / 2) - 1)

        topright = (topright[0] / (self.engine.window_width / 2) - 1,
                    topright[1] / (self.engine.window_height / 2) - 1)

        return (*bottomleft, *bottomright, *topleft, *topright)
    
    @contextmanager
    def no_depth_test(self):
        """ Render without depth test. """

        self.context.disable(moderngl.DEPTH_TEST)
        
        try: yield None

        finally:
            self.context.enable(moderngl.DEPTH_TEST)

    def draw_shadow_text(self,
            surface: pygame.Surface,
            font: pygame.font.Font,
            text: str,
            pos: tuple[int, int],
            color: tuple[float, float, float],
            shadow_offset: int = 1
            ):
        """
        Draw text with shadow on a Pygame surface.

        @param text Text to draw
        @param pos Position on surface
        @param color Color of text
        @param shadow_offset Distance of shadow from the text
        """

        shadow = font.render(text, True, (0, 0, 0)).convert_alpha()
        offsets = (
            (pos[0] - shadow_offset, pos[1]),
            (pos[0] + shadow_offset, pos[1]),
            (pos[0],                 pos[1] + shadow_offset),
            (pos[0],                 pos[1] - shadow_offset)
        )
        for p in offsets:
            surface.blit(shadow, p)

        surface.blit(font.render(text, True, color), pos)
    
    def clear(self):
        """ Clear active framebuffer. """
        self.context.clear(*self.clear_color)

    def to_buffer(self, array: list) -> bytes:
        """ Convert array to ModernGL compatible buffer form. """
        dtype = "f" if isinstance(array[0], float) else "I"
        return struct.pack(f"{len(array)}{dtype}", *array)

    def create_bo(self, array: list) -> moderngl.Buffer:
        """ Create buffer object from array. """
        return self.context.buffer(self.to_buffer(array))
    
    def get_shader(self, 
            shader: str,
            force: bool = False
            ) -> moderngl.Program:
        """
        This function caches shader programs which can be used commonly for future use.
        If it can't be used commonly it creates a new instance and returns it.

        @param force Force compile all common shader programs
        @return Shader program
        """

        # Common shader programs
        if len(self.__programs) == 0 or force:
            self.__programs.clear()

            self.__programs["base"] = self.context.program(
                vertex_shader = open(source_path("goldsrc", "shaders", "base.vsh")).read(),
                fragment_shader = open(source_path("goldsrc", "shaders", "base.fsh")).read()
            )

            self.__programs["unlit"] = self.context.program(
                vertex_shader = open(source_path("goldsrc", "shaders", "base.vsh")).read(),
                fragment_shader = open(source_path("goldsrc", "shaders", "unlit.fsh")).read()
            )

            self.__programs["normal"] = self.context.program(
                vertex_shader = open(source_path("goldsrc", "shaders", "normal.vsh")).read(),
                fragment_shader = open(source_path("goldsrc", "shaders", "normal.fsh")).read()
            )

            self.__programs["skybox"] = self.context.program(
                vertex_shader = open(source_path("goldsrc", "shaders", "skybox.vsh")).read(),
                fragment_shader = open(source_path("goldsrc", "shaders", "skybox.fsh")).read()
            )

            self.__programs["ui"] = self.context.program(
                vertex_shader = open(source_path("goldsrc", "shaders", "ui.vsh")).read(),
                fragment_shader = open(source_path("goldsrc", "shaders", "ui.fsh")).read()
            )

            self.__programs["gaussian_blur"] = self.context.program(
                vertex_shader = open(source_path("goldsrc", "shaders", "ui.vsh")).read(),
                fragment_shader = open(source_path("goldsrc", "shaders", "gaussian_blur.fsh")).read()
            )

        # Non common shader programs
        if shader == "flat":
            return self.context.program(
                vertex_shader = open(source_path("goldsrc", "shaders", "base.vsh")).read(),
                fragment_shader = open(source_path("goldsrc", "shaders", "flat.fsh")).read()
            )
        
        elif shader == "unlitflat":
            return self.context.program(
                vertex_shader = open(source_path("goldsrc", "shaders", "base.vsh")).read(),
                fragment_shader = open(source_path("goldsrc", "shaders", "unlitflat.fsh")).read()
            )

        return self.__programs[shader]
    
    def setup_postprocess(self):
        """ Setup postprocess. """

        self.postprocess = Widget(
            self.ui,
            (0, 0),
            (self.engine.window_width, self.engine.window_height),
            program_name="gaussian_blur"
        )
    
    def setup_debug_ui(self):
        """ Setup debug UI."""
        
        self.debug_ui = Widget(self.ui, (0, 0), (305, 155))

        self.debug_ui_font = pygame.font.Font(source_path("assets", "fonts", "FiraCode.ttf"), 12)
        self.debug_ui_font.set_bold(True)
    
    def render_debug_ui(self):
        """ Render debug UI. """

        self.debug_ui.surface.fill((0, 0, 0, 130))

        y_gap = 16
        row_start = 65
        row_gap = 45
        label_color = (255, 255, 255)
        avg_color = (255, 241, 115)
        min_color = (121, 255, 94)
        max_color = (255, 101, 87)
        cpu_color = (112, 212, 255)
        gpu_color = (255, 144, 99)
        version_color = (138, 255, 208)

        # Prevent OverflowError
        if self.engine.fps == float("inf"):
            self.engine.fps = 0

        # Draw FPS stats
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "FPS", (5, 5 + y_gap * 0),
            label_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(round(self.engine.fps_avg)),
            (row_start + row_gap * 0, 5 + y_gap * 0),
            avg_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(round(self.engine.fps_max)),
            (row_start + row_gap * 1, 5 + y_gap * 0),
            min_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(round(self.engine.fps_min)),
            (row_start + row_gap * 2, 5 + y_gap * 0),
            max_color
        )

        # Draw frame time stats
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "Frame", (5, 5 + y_gap * 1),
            label_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(round(self.engine.frame_time_avg * 1000, 2)),
            (row_start + row_gap * 0, 5 + y_gap * 1),
            avg_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(round(self.engine.frame_time_min * 1000, 2)),
            (row_start + row_gap * 1, 5 + y_gap * 1),
            min_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(round(self.engine.frame_time_max * 1000, 2)),
            (row_start + row_gap * 2, 5 + y_gap * 1),
            max_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "ms",
            (row_start + row_gap * 3, 5 + y_gap * 1),
            label_color
        )

        # Draw render time stats
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "Render", (5, 5 + y_gap * 2),
            label_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(round(self.engine.render_time_avg * 1000, 2)),
            (row_start + row_gap * 0, 5 + y_gap * 2),
            avg_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(round(self.engine.render_time_min * 1000, 2)),
            (row_start + row_gap * 1, 5 + y_gap * 2),
            min_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(round(self.engine.render_time_max * 1000, 2)),
            (row_start + row_gap * 2, 5 + y_gap * 2),
            max_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "ms",
            (row_start + row_gap * 3, 5 + y_gap * 2),
            label_color
        )

        # Draw hardware info
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            self.engine.cpu_info["name"],
            (5, 5 + y_gap * 3),
            cpu_color
        )

        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            self.engine.gpu_info["name"],
            (5, 5 + y_gap * 4),
            gpu_color
        )

        # Display info
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "Display",
            (5, 5 + y_gap * 5),
            label_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            f"{self.engine.window_width}x{self.engine.window_height}",
            (60, 5 + y_gap * 5),
            avg_color
        )

        # Draw version info
        is_python_64bit = sys.maxsize > 2**32
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "Python",
            (5, 5 + y_gap * 6),
            label_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            f"{platform.python_version()}, {('32', '64')[is_python_64bit]}-bit",
            (row_start - 12, 5 + y_gap * 6),
            version_color
        )

        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "Pygame",
            (5, 5 + y_gap * 7),
            label_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(self.engine.pygame_version),
            (row_start - 12, 5 + y_gap * 7),
            version_color
        )

        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "SDL",
            (5 + 105, 5 + y_gap * 7),
            label_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(self.engine.sdl_version),
            (row_start + 70, 5 + y_gap * 7),
            version_color
        )

        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "ModernGL",
            (5, 5 + y_gap * 8),
            label_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(self.engine.moderngl_version),
            (row_start, 5 + y_gap * 8),
            version_color
        )

        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            "OpenGL",
            (5 + 105, 5 + y_gap * 8),
            label_color
        )
        self.draw_shadow_text(
            self.debug_ui.surface,
            self.debug_ui_font,
            str(self.engine.opengl_version),
            (row_start + 91, 5 + y_gap * 8),
            version_color
        )

        # Update debug UI texture
        self.debug_ui.update_texture()

        # Render debug UI
        self.debug_ui.render()