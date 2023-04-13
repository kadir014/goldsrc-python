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


class Menu(Scene):
    def __init__(self, engine: Engine):
        super().__init__(engine)

        self.engine.disable_virtual_mouse()

        self.engine.renderer.clear_color = self.engine.renderer.normalize_color((200, 200, 255))

        self.ui = Container(self.engine)

        self.test_widget = Widget(self.ui, (0, 0), (1280, 720))