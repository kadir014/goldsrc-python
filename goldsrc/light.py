"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import Optional

import glm


class BasicLight:
    """
    Basic phong (ambient & diffuse & specular) lighting.
    """
    
    def __init__(self,
            position: glm.vec3,
            color: Optional[glm.vec3] = None,
            ambient_intensity: float = 0.03,
            diffuse_intensity: float = 0.7,
            specular_intensity: float = 0.8,
            specular_power: float = 32.0
            ):
        self.position = position
        
        if color is None:
            color = glm.vec3(1.0, 1.0, 1.0)

        self.color = color

        self.ambient_intensity = ambient_intensity
        self.diffuse_intensity = diffuse_intensity
        self.specular_intensity = specular_intensity
        self.specular_power = specular_power