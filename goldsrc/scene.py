"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import Engine
    from .entity import Entity
    

class Scene:
    """
    Base scene class.
    """

    def __init__(self, engine: "Engine"):
        self.engine = engine

        # Active camera
        self.camera = None

        # Active skybox
        self.skybox = None

        # Active UI container
        self.ui = None

        self.entities = []
        self.light = None

    def add_entity(self, entity: "Entity"):
        """ Add model to the scene. """
        self.entities.append(entity)

    def update(self):
        """ Scene update callback. """
        NotImplemented

    def render(self):
        """ Scene render callback. """
        NotImplemented