"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine import Engine


class Container:
    """
    Container for UI widgets that stores and manages them.
    """

    def __init__(self, engine: "Engine"):
        self.engine = engine
        self.widgets = []

    def update(self):
        """ Update widgets. """
        for widget in self.widgets:
            if widget.enabled: widget.update()

    def render(self):
        """ Render widgets. """
        for widget in self.widgets:
            if widget.enabled: widget.render()