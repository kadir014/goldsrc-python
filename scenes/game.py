"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from math import radians, sin, cos, pi
from random import choice
from time import time

import glm
import pygame

from goldsrc import (
    Engine,
    Scene,
    Entity,
    BasicModel,
    MultiMaterialModel,
    BasicAnimatedModel,
    MultiMaterialAnimatedModel,
    Camera,
    BasicLight,
    Skybox
)
from goldsrc.path import source_path
from goldsrc.ui import Container, Widget


class Player(Entity):
    def __init__(self, engine: "Engine", position: glm.vec3):
        super().__init__(engine, position=position)

        self.velocity = glm.vec3(0.0)
        self.on_ground = False

        self.movement_speed = 0.9
        self.jump_speed = 9.0
        self.ground_friction = 0.88
        self.air_friction = 0.88

        self.height = 1.78

        self.walk_sounds = [
            pygame.mixer.Sound(source_path("assets", "sounds", "pl_dirt1.wav")),
            pygame.mixer.Sound(source_path("assets", "sounds", "pl_dirt2.wav")),
            pygame.mixer.Sound(source_path("assets", "sounds", "pl_dirt3.wav")),
            pygame.mixer.Sound(source_path("assets", "sounds", "pl_dirt4.wav"))
        ]
        self.last_played = time()
        self.walk_sound_duration = 0.33

        self.engine.master_volume = 0.4
        for sound in self.walk_sounds:
            sound.set_volume(self.engine.master_volume)

    def update(self, *args):
        super().update(*args)

        movement_key = False

        # Read inputs if settings menu is not shown
        if not self.engine.scene.settings.enabled:
            accel = self.movement_speed * self.engine.dt
            xa = cos(self.engine.scene.camera.yaw) * accel
            za = sin(self.engine.scene.camera.yaw) * accel
            xsa = cos(self.engine.scene.camera.yaw + pi/2) * accel
            zsa = sin(self.engine.scene.camera.yaw + pi/2) * accel

            if self.engine.input.key_held("w"):
                movement_key = True
                self.velocity.x += xa
                self.velocity.z += za

            if self.engine.input.key_held("s"):
                movement_key = True
                self.velocity.x -= xa
                self.velocity.z -= za

            if self.engine.input.key_held("a"):
                movement_key = True
                self.velocity.x -= xsa
                self.velocity.z -= zsa

            if self.engine.input.key_held("d"):
                movement_key = True
                self.velocity.x += xsa
                self.velocity.z += zsa

            if self.engine.input.key_pressed("space") and self.on_ground:
                self.on_ground = False
                self.velocity.y += self.jump_speed * self.engine.dt

        gravity = -9.81 * 2.0 / 100.0 * self.engine.dt
        self.velocity.y += gravity

        # Solve ground collision
        penatration = -4.0 - (self.position.y - self.height)
        if self.position.y - self.height + self.velocity.y < -4.0:
            self.velocity.y = 0
            self.position.y += penatration

            # Play landing sound
            now = time()
            if (not movement_key or self.engine.input.key_held("space")) and not \
                self.on_ground and now - self.last_played > self.walk_sound_duration:
                choice(self.walk_sounds).play()
                self.last_played = now

            self.on_ground = True

            # Bunny hopping
            if self.engine.input.key_held("space") and not self.engine.scene.settings.enabled:
                self.on_ground = False
                self.velocity.y += self.jump_speed * self.engine.dt

        # Apply friction
        self.velocity.x *= self.ground_friction if self.on_ground else self.air_friction
        self.velocity.z *= self.ground_friction if self.on_ground else self.air_friction

        # Integrate velocity
        self.position += self.velocity

        # Play walking sound
        now = time()
        if movement_key and self.on_ground and now - self.last_played > self.walk_sound_duration:
            choice(self.walk_sounds).play()
            self.last_played = now


class Button(Widget):
    """
    Button widget.
    """

    def __init__(self,
            container: Container,
            position: tuple[float, float],
            size: tuple[int, int],
            label: str
            ):
        super().__init__(container, position, size)

        # States
        # These are not private but no reason to access them manually
        self.hovered = False
        self.pressed = False
        self.toggled = False

        self.clicked = None

        self.label = label
        # TODO: Do not load fonts for every instance and find a better way to handle them
        self.font = pygame.font.Font(source_path("assets", "fonts", "Montserrat-Regular.ttf"), 16)

        # TODO: Again, do not load resources for every instance
        self.hover_sound = pygame.mixer.Sound(source_path("assets", "sounds", "mouse_hover.mp3"))
        self.click_sound = pygame.mixer.Sound(source_path("assets", "sounds", "mouse_click.ogg"))

        # Create the initial surface
        self.draw()

    def update(self):
        """ Update widget. """

        mouse = self.container.engine.mouse

        # Check if mouse is inside button's bounds
        if pygame.Rect(self.position, self.size).collidepoint(mouse.x, mouse.y):
            if not self.hovered:
                self.hovered = True
                self.hover_sound.play()
                self.draw()

        elif self.hovered:
            self.hovered = False
            self.draw()

        # Check pressing events
        for event in self.container.engine.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.hovered:
                        self.pressed = True
                        self.draw()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.pressed:
                        self.pressed = False
                        self.draw()
                        if self.clicked is not None:
                            self.click_sound.play()
                            self.clicked(self)

    def draw(self):
        """ Draw the widget display. """

        if self.toggled:
            self.surface.fill((70, 70, 70, 170))
            self.surface.fill((255, 180, 0), (0, 0, 5, self.surface.get_height()))

        elif self.pressed:
            self.surface.fill((100, 100, 100, 170))
            
        elif self.hovered:
            self.surface.fill((40, 40, 40, 170))

        else:
            self.surface.fill((0, 0, 0, 170))

        label = self.font.render(self.label, True, (255, 255, 255))
        self.surface.blit(label, (15, 5))

        self.update_texture()


class HorizontalSwitch(Widget):
    """
    Horionztal switch widget.
    """

    def __init__(self,
            container: Container,
            position: tuple[float, float],
            size: tuple[float, float],
            values: list[str],
            default: int,
            loop: bool = True
            ):
        super().__init__(container, position, size)

        self.values = values
        self.cursor = default
        self.loop = loop

        # TODO
        self.font = pygame.font.Font(source_path("assets", "fonts", "Montserrat-Regular.ttf"), 16)
        self.larrow = pygame.image.load(source_path("assets", "textures", "arrow.png")).convert_alpha()
        self.rarrow = pygame.transform.flip(self.larrow, True, False)

        self.draw()

        self.hovered = False
        self.pressed = False
        self.pressed_side = 0

    def update(self):
        """ Update widget. """

        mouse = self.container.engine.mouse

        # Check if mouse is inside button's bounds
        if pygame.Rect(self.position, self.size).collidepoint(mouse.x, mouse.y):
            if not self.hovered:
                self.hovered = True

        elif self.hovered:
            self.hovered = False

        # Check pressing events
        for event in self.container.engine.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.hovered:
                        self.pressed = True

                        if mouse.x < self.position[0] + 20:
                            self.pressed_side = 0

                        elif mouse.x > self.position[0] + self.size[0] - 20:
                            self.pressed_side = 1
                        
                        else:
                            self.pressed_side = -1

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.pressed:
                        self.pressed = False

                        if self.pressed_side == 0:
                            self.cursor -= 1
                            if self.cursor < 0:
                                if self.loop: self.cursor = len(self.values) - 1
                                else: self.cursor = 0

                            self.draw()

                        if self.pressed_side == 1:
                            self.cursor += 1
                            if self.cursor > len(self.values) - 1:
                                if self.loop: self.cursor = 0
                                else: self.cursor = len(self.values) - 1

                            self.draw()

    def draw(self):
        self.surface.fill((0, 0, 0, 0))

        text = self.font.render(self.values[self.cursor], True, (255, 255, 255))
        self.surface.blit(
            text,
            (self.size[0] / 2 - text.get_width() / 2, 0)
        )

        self.surface.blit(self.larrow, (5, 3))
        self.surface.blit(self.rarrow, (self.size[0] - 9 - 5, 3))

        self.update_texture()


class DropDown(Widget):
    """
    Drop down menu widget.
    """

    def __init__(self,
            container: Container,
            position: tuple[float, float],
            size: tuple[float, float]
            ):
        super().__init__(container, position, size)


class GraphicsSettings(Widget):
    """
    Graphics settings.
    """

    def __init__(self,
            container: Container,
            position: tuple[float, float],
            size: tuple[float, float]
            ):
        super().__init__(container, position, size)

        # TODO
        self.font = pygame.font.Font(source_path("assets", "fonts", "Montserrat-Regular.ttf"), 16)

        self.text_layer = pygame.Surface(self.size, pygame.SRCALPHA).convert_alpha()

        self.settings = {}

        start_y = 7
        gap_y = 27

        w_width = 250

        display_text = self.font.render("DISPLAY", True, (255, 180, 0))
        self.text_layer.blit(
            display_text,
            (self.size[0] / 2 - display_text.get_width() / 2, start_y)
        )

        pygame.draw.line(
            self.text_layer,
            (255, 180, 0),
            (25, start_y + gap_y * 1),
            (self.size[0] - 26, start_y + gap_y * 1)
        )

        start_y = -11
        gap_y = 30

        # Fullscreen [on, off]

        self.settings["fullscreen"] = (25, start_y + gap_y * 2)

        self.text_layer.blit(
            self.font.render("Fullscreen", True, (255, 255, 255)),
            (25, start_y + gap_y * 2)
        )

        self.hswitch_fullscreen = HorizontalSwitch(
            self.container,
            (
                self.position[0] + self.size[0] - w_width - 30,
                self.position[1] + start_y + gap_y * 2
            ),
            (w_width, 30),
            values=("On", "Off"),
            default=1
        )

        # Resolution [combo box]

        self.settings["resolution"] = (25, start_y + gap_y * 3)

        self.text_layer.blit(
            self.font.render("Resolution", True, (255, 255, 255)),
            (25, start_y + gap_y * 3)
        )

        # VSync [on, off]

        self.settings["vsync"] = (25, start_y + gap_y * 4)

        self.text_layer.blit(
            self.font.render("VSync", True, (255, 255, 255)),
            (25, start_y + gap_y * 4)
        )

        self.hswitch_vsync = HorizontalSwitch(
            self.container,
            (
                self.position[0] + self.size[0] - w_width - 30,
                self.position[1] + start_y + gap_y * 4
            ),
            (w_width, 30),
            values=("On", "Off"),
            default=1
        )

        # FPS limit [combo box]

        self.settings["fps-limit"] = (25, start_y + gap_y * 5)

        self.text_layer.blit(
            self.font.render("FPS limit", True, (255, 255, 255)),
            (25, start_y + gap_y * 5)
        )

        start_y = 7
        gap_y = 27

        display_text = self.font.render("ADVANCED", True, (255, 180, 0))
        self.text_layer.blit(
            display_text,
            (self.size[0] / 2 - display_text.get_width() / 2, start_y + gap_y * 6)
        )

        pygame.draw.line(
            self.text_layer,
            (255, 180, 0),
            (25, start_y + gap_y * 7),
            (self.size[0] - 26, start_y + gap_y * 7)
        )

        start_y = -30
        gap_y = 30

        # MSAA [Off 2x 4x 8x 16x]

        self.settings["msaa"] = (25, start_y + gap_y * 8)

        self.text_layer.blit(
            self.font.render("MSAA", True, (255, 255, 255)),
            (25, start_y + gap_y * 8)
        )

        self.hswitch_msaa = HorizontalSwitch(
            self.container,
            (
                self.position[0] + self.size[0] - w_width - 30,
                self.position[1] + start_y + gap_y * 8
            ),
            (w_width, 30),
            values=("Off", "2x", "4x", "8x", "16x"),
            default=4
        )

        # Anisotropic filtering [Off 2x 4x 8x 16x]

        self.settings["anisotropic"] = (25, start_y + gap_y * 9)
        
        self.text_layer.blit(
            self.font.render("Anisotropic filtering", True, (255, 255, 255)),
            (25, start_y + gap_y * 9)
        )

        self.hovered_setting = None
        
        self.draw()

    def update(self):
        mouse = self.container.engine.mouse

        hovered = False

        if self.position[0] < mouse.x < self.position[0] + self.size[0]:
            for setting in self.settings:
                rect = pygame.Rect(self.position[0], self.position[1]+self.settings[setting][1]-5, self.size[0], 30)
                if rect.collidepoint(mouse.x, mouse.y):
                    hovered = True
                    if self.hovered_setting == setting: break
                    self.hovered_setting = setting
                    self.draw()
                    break

        if not hovered and self.hovered_setting is not None:
            self.hovered_setting = None
            self.draw()


    def draw(self):
        self.surface.fill((0, 0, 0, 170))

        if self.hovered_setting is not None:
            s = self.settings[self.hovered_setting]
            self.surface.fill((60, 60, 60, 170), (0, s[1]-5, self.size[0], 30))

        self.surface.blit(self.text_layer, (0, 0))

        self.update_texture()


class Settings(Widget):
    """
    Settings menu UI.
    """

    def __init__(self,
            container: Container,
            position: tuple[float, float],
            size: tuple[float, float]
            ):
        super().__init__(container, position, size)

        self.surface.fill((0, 0, 0, 77))
        self.update_texture()

        menu_x = 200
        menu_y = 100
        menu_y_gap = 5 + 30

        # Create menu buttons
        self.menu_game = Button(self.container, (menu_x, menu_y), (150, 30), "Game")
        self.menu_controls = Button(self.container, (menu_x, menu_y+ menu_y_gap * 1), (150, 30), "Controls")
        self.menu_graphics = Button(self.container, (menu_x, menu_y + menu_y_gap * 2), (150, 30), "Graphics")
        self.menu_audio = Button(self.container, (menu_x, menu_y + menu_y_gap * 3), (150, 30), "Audio")

        # Set game menu as the defualt toggled button
        self.menu_toggled = self.menu_game
        self.menu_toggled.toggled = True
        self.menu_toggled.draw()

        def menu_clicked(menu_button: Button):
            # Update the old toggled button
            self.menu_toggled.toggled = False
            self.menu_toggled.draw()

            # Set new clicked button as the toggled one
            self.menu_toggled = menu_button
            self.menu_toggled.toggled = True
            self.menu_toggled.draw()

        # Set all menu butttons' callbacks
        self.menu_game.clicked = menu_clicked
        self.menu_controls.clicked = menu_clicked
        self.menu_graphics.clicked = menu_clicked
        self.menu_audio.clicked = menu_clicked

        self.settings_graphics = GraphicsSettings(
            self.container,
            (menu_x + 150 + 5, menu_y),
            (725, 539)
        )

    def toggle_enabled(self):
        self.enabled = not self.enabled
        self.menu_game.enabled = self.enabled
        self.menu_controls.enabled = self.enabled
        self.menu_graphics.enabled = self.enabled
        self.menu_audio.enabled = self.enabled
        self.settings_graphics.enabled = self.enabled
        self.settings_graphics.hswitch_fullscreen.enabled = self.enabled
        self.settings_graphics.hswitch_vsync.enabled = self.enabled
        self.settings_graphics.hswitch_msaa.enabled = self.enabled


class Game(Scene):
    def __init__(self, engine: Engine):
        super().__init__(engine)

        self.engine.enable_virtual_mouse()

        self.camera = Camera(self.engine.aspect_ratio)

        self.light = BasicLight(glm.vec3(0.0, 3.0, 0.0), ambient_intensity = 0.1)

        self.skybox = Skybox(
            self.engine,
            {
                "xneg": source_path("assets", "skybox", "2desert_xneg.png"),
                "xpos": source_path("assets", "skybox", "2desert_xpos.png"),
                "yneg": source_path("assets", "skybox", "2desert_yneg.png"),
                "ypos": source_path("assets", "skybox", "2desert_ypos.png"),
                "zneg": source_path("assets", "skybox", "2desert_zneg.png"),
                "zpos": source_path("assets", "skybox", "2desert_zpos.png"),
            }
        )

        light_bulb_model = BasicModel.from_obj(
            self.engine,
            source_path("assets", "models", "sphere.obj"),
            program_name="unlitflat"
        )
        self.light_bulb = Entity(
            self.engine,
            position=glm.vec3(0.0, 3.0, 0.0),
            model=light_bulb_model
        )
        self.add_entity(self.light_bulb)

        ground_model = BasicModel.from_plane(
            self.engine,
            15.0,
            texture_path=source_path("assets", "textures", "OUT_SDN2B.png")
        )

        self.ground = Entity(
            self.engine,
            position=glm.vec3(0.0, -4.0, 0.0),
            model=ground_model
        )
        self.ground.rotation.x += pi / 2
        self.add_entity(self.ground)

        box_model = BasicModel.from_cube(
            self.engine,
            1.5,
            texture_path=source_path("assets", "textures", "crate.png"),
            color=glm.vec4(0.5, 0.0, 1.0, 1.0)
        )

        self.box = Entity(
            self.engine,
            position=glm.vec3(5.0, -2.5, 0.0),
            model=box_model
        )
        self.add_entity(self.box)

        headcrab_model = MultiMaterialAnimatedModel.from_obja(
            self.engine,
            source_path("assets", "animations", "headcrab_idle1.obja")
        )
        self.headcrab = Entity(
            self.engine,
            position=glm.vec3(-3.0, -4.0, -3.0),
            model=headcrab_model
        )
        self.add_entity(self.headcrab)
        self.headcrab.scale /= 10.0
        headcrab_model.play(loop=True)

        brick_model = BasicAnimatedModel.from_obja(
            self.engine,
            source_path("assets", "animations", "sequence.obja"),
            program_name="flat"
        )
        self.brick = Entity(
            self.engine,
            position=glm.vec3(-10.0, 0.0, 0.0),
            model=brick_model
        )
        self.brick.rotation.y = 0.7
        self.add_entity(self.brick)
        brick_model.play(loop=True)

        self.player = Player(self.engine, glm.vec3(0.0))
        self.add_entity(self.player)

        self.ui = Container(self.engine)

        self.settings = Settings(self.ui, (0, 0), (1280, 720))
        self.settings.toggle_enabled()

    def update(self):
        if self.engine.input.key_pressed("escape"):
            self.settings.toggle_enabled()

            # Enable gaussian blur when settings menu is open
            #self.engine.apply_postprocess = self.settings.enabled

            if self.settings.enabled:
                self.engine.disable_virtual_mouse()
            else:
                self.engine.enable_virtual_mouse()

        if not self.settings.enabled:
            offset = self.engine.mouse_rel
            offset *= 0.15

            self.camera.yaw += radians(offset.x)
            self.camera.pitch -= radians(offset.y)

            self.camera.position = self.player.position

        if self.engine.input.key_pressed("f1"):
            self.engine.show_debug_ui = not self.engine.show_debug_ui

