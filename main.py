"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

import os
os.environ["PY_USED_FREEZER"] = "none" # For setting up PyInstaller or cx_Freeze

from goldsrc import Engine
from scenes.game import Game


if __name__ == "__main__":
    engine = Engine()

    engine.add_scene(Game(engine))

    engine.run()