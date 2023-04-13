"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import Union

from time import perf_counter
from pathlib import Path
from contextlib import contextmanager

import pygame
import moderngl

from .common import DISPLAY_RESOLUTIONS
from .renderer import Renderer
from .input import InputManager
from .scene import Scene
from .hwinfo import get_cpu_info, get_gpu_info
from .path import source_path


class Engine:
    """
    Core engine class.
    """

    def __init__(self):
        # Events & timing
        self.events = []
        self.clock = pygame.time.Clock()
        self.max_fps = 165
        self.fps = self.max_fps
        self.dt = 1.0 / self.fps
        self.is_running = False
        self.counter = 0

        # Audio
        self.master_volume = 1.0

        # Create input manager
        self.input = InputManager(self)

        # Get monitor size
        pygame.display.init() # Initialize display to get display info
        display_info = pygame.display.Info()
        self.monitor_width = display_info.current_w
        self.monitor_height = display_info.current_h

        # Window attributes
        resolution = self.get_max_resolution(self.get_monitor_aspect_ratio())
        self.window_width = resolution[0]
        self.window_height = resolution[1]
        self.__window_title = ""

        # Create renderer
        self.renderer = Renderer(self)
        self.renderer.setup_debug_ui()
        self.renderer.setup_postprocess()

        # Rendering settings
        self.apply_postprocess = False
        self.show_debug_ui = False

        # Scenes
        self.scenes = {}
        self.__current_scene = None

        # Version info
        self.version = (0, 0, 0)
        self.version_string = ".".join((str(v) for v in self.version))
        self.pygame_version = pygame.version.ver
        self.sdl_version = ".".join((str(v) for v in pygame.get_sdl_version()))
        self.moderngl_version = moderngl.__version__
        self.opengl_version = self.renderer.context.version_code

        # Get hardware info
        self.cpu_info = get_cpu_info()
        self.gpu_info = get_gpu_info(self.renderer.context)

        # Profiling stuff
        self.fps_avg = 0.0
        self.fps_min = 0.0
        self.fps_max = 0.0
        self.__fpss = []
        self.frame_time = 0.0
        self.frame_time_avg = 0.0
        self.frame_time_min = 0.0
        self.frame_time_max = 0.0
        self.__frame_times = []
        self.render_time = 0.0
        self.render_time_avg = 0.0
        self.render_time_min = 0.0
        self.render_time_max = 0.0
        self.__render_times = []

        # Set window defaults
        self.window_title = "GoldSrc Python"
        self.set_icon(source_path("assets", "windowicon.png"))

    @property
    def window_title(self):
        return self.__window_title
    
    @window_title.setter
    def window_title(self, new_title: str):
        self.__window_title = new_title
        pygame.display.set_caption(self.__window_title)

    def set_window_size(self, size: tuple[int, int]):
        """ Set window size. """

        self.window_width, self.window_height = size

        self.renderer.create_window()

    @property
    def aspect_ratio(self) -> float:
        return self.window_width / self.window_height

    def set_icon(self, filepath: Union[Path, str]):
        """ Set window icon. """
        pygame.display.set_icon(pygame.image.load(filepath))

    def get_monitor_aspect_ratio(self) -> str:
        """ Get aspect ratio of the monitor. """

        monitor_tuple = (self.monitor_width, self.monitor_height)

        if monitor_tuple in DISPLAY_RESOLUTIONS["16:9"]:
            return "16:9"
        
        elif monitor_tuple in DISPLAY_RESOLUTIONS["4:3"]:
            return "4:3"

    def get_usable_resolutions(self) -> dict:
        """ Get usable resolutions on the monitor. """

        resolutions = {"16:9": [], "4:3": []}

        for res in DISPLAY_RESOLUTIONS["16:9"]:
            if res[0] <= self.monitor_width and res[1] <= self.monitor_height:
                resolutions["16:9"].append(res)

        for res in DISPLAY_RESOLUTIONS["4:3"]:
            if res[0] <= self.monitor_width and res[1] <= self.monitor_height:
                resolutions["4:3"].append(res)

        return resolutions
    
    def get_max_resolution(self, aspect_ratio: str) -> tuple[int, int]:
        """ Get maximum usable resolution on the monitor. """

        resolutions = self.get_usable_resolutions()

        return resolutions[aspect_ratio][-1]
    
    @property
    def scene(self) -> Scene:
        """ Get the current scene. """
        return self.scenes[self.__current_scene]
    
    def add_scene(self, scene: Scene):
        """
        Add a scene to the engine.
        This function also sets the current scene as the last added one.
        """
        self.__current_scene = scene.__class__.__name__
        self.scenes[self.__current_scene] = scene
    
    def enable_virtual_mouse(self):
        """ Enable virtual mouse. """
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    def disable_virtual_mouse(self):
        """ Disable virtual mouse. """
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
    
    def handle_events(self):
        """ Handle Pygame events. """

        self.events = pygame.event.get()

        for event in self.events:
            if event.type == pygame.QUIT:
                self.stop()

        self.input.update()

    @contextmanager
    def profile(self, mode: str):
        """ Profile code. """

        start = perf_counter()
        
        try: yield None

        finally:
            if mode == "render":
                self.render_time += perf_counter() - start

            elif mode == "frame":
                self.frame_time = perf_counter() - start

    def stop(self):
        """ Stop the engine. """
        self.is_running = False

    def run(self):
        """ Run the engine. """
        self.is_running = True

        # Warmup clock
        # I don't remember where I saw this trick or don't know even if it's useful
        for _ in range(10): self.clock.tick(self.max_fps)

        while self.is_running:
            self.dt = self.clock.tick(self.max_fps) / 1000
            self.fps = self.clock.get_fps()

            with self.profile("frame"):

                self.handle_events()

                self.mouse = pygame.Vector2(*pygame.mouse.get_pos())
                self.mouse_rel = pygame.Vector2(*pygame.mouse.get_rel())

                # Update scene
                self.scene.update()
                
                # Update scene's active camera
                if self.scene.camera is not None:
                    self.scene.camera.update()

                # Time spent on rendering this frame
                self.render_time = 0.0

                if self.apply_postprocess:
                    self.renderer.game_fbo.use()
                    self.renderer.clear()

                else:
                    self.renderer.context.screen.use()
                    self.renderer.clear()

                # Update and render scene's active skybox
                if self.scene.skybox is not None:
                    self.scene.skybox.update(self.scene.camera)

                    with self.profile("render"):
                        with self.renderer.no_depth_test():
                            self.scene.skybox.render()

                # Update and render models
                for entity in self.scene.entities:
                    entity.update(self.scene.camera, self.scene.light)

                    if entity.model is not None:
                        with self.profile("render"):
                            if entity.model.program_name == "base":pass
                                #model.program["s_skybox"] = 0
                            #entity.model.program["s_texture"] = 0
                            #if entity.model.normal_map is not None:
                            #    entity.model.program["s_texture"] =0
                            #    entity.model.program["s_normal"] = 1
                            entity.model.render()

                with self.profile("render"):
                    # Render scene
                    self.scene.render()

                    # Render post-processing effect
                    if self.apply_postprocess:
                        self.renderer.context.screen.use()
                        self.renderer.clear()

                        self.renderer.game_fbo.color_attachments[0].use()
                        self.renderer.postprocess.vao.render()

                    # Render scene UI
                    if self.scene.ui is not None:
                        self.scene.ui.update()
                        self.scene.ui.render()

                    # Render debug UI
                    if self.show_debug_ui:
                        self.renderer.render_debug_ui()

                    # Update display
                    pygame.display.flip()

            # Update profiling stats

            self.__fpss.append(self.fps)
            if len(self.__fpss) > 60:
                self.__fpss.pop(0)

            self.__frame_times.append(self.frame_time)
            if len(self.__frame_times) > 60:
                self.__frame_times.pop(0)

            self.__render_times.append(self.render_time)
            if len(self.__render_times) > 60:
                self.__render_times.pop(0)

            self.counter += 1
            if self.counter % 60 == 0:
                self.fps_avg = sum(self.__fpss) / len(self.__fpss)
                self.fps_min = min(self.__fpss)
                self.fps_max = max(self.__fpss)
                self.frame_time_avg = sum(self.__frame_times) / len(self.__frame_times)
                self.frame_time_min = min(self.__frame_times)
                self.frame_time_max = max(self.__frame_times)
                self.render_time_avg = sum(self.__render_times) / len(self.__render_times)
                self.render_time_min = min(self.__render_times)
                self.render_time_max = max(self.__render_times)

        # Release resources
        pygame.quit()
        self.renderer.context.release()