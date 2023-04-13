"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import Union

from math import sin, cos, radians, pi

import glm


class Camera:
    """
    Base camera class.
    """

    def __init__(self,
            aspect_ratio: float,
            fov: float = 90.0,
            position: Union[tuple[float, float, float], glm.vec3] = (0.0, 0.0, 0.0),
            is_ortho: bool = False,
            near: float = 0.1,
            far: float = 1000.0
            ):
        self.is_ortho = is_ortho

        # View planes
        self.near = near
        self.far = far

        self.aspect_ratio = aspect_ratio
        self.__fov = fov
        self.fov = self.__fov # Set projection matrix
        self.position = glm.vec3(position)

        # For view matrix
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.up    = glm.vec3(0.0, 1.0,  0.0)
        self.right = glm.vec3(1.0, 0.0,  0.0)

        # Orientation
        self.yaw = -pi / 2
        self.pitch = 0

        #self.update()

    def get_view_matrix(self) -> glm.mat4:
        """
        Generate view matrix

        up
        ^
        |

        eye  --->  center
        """

        return glm.lookAt(
            self.position,
            self.position + self.front,
            self.up
        )

    def update(self):
        """ Update vectors used to generate view matrix. """
        if self.pitch > pi / 2: self.pitch = pi / 2
        if self.pitch < -pi / 2: self.pitch = -pi / 2
        
        front = glm.vec3(0.0, 0.0, 0.0)
        front.x = cos(self.yaw) * cos(self.pitch)
        front.y = sin(self.pitch)
        front.z = sin(self.yaw) * cos(self.pitch)

        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, glm.vec3(0.0, 1.0, 0.0)))
        self.up    = glm.normalize(glm.cross(self.right, self.front))

    @property
    def fov(self):
        return self.__fov

    @fov.setter
    def fov(self, new_fov):
        self.__fov = new_fov

        # Recreate the projection matrix

        if self.is_ortho:
            self.projection = glm.ortho(-1280/100.0, 1280/100.0, -720/100.0, 720/100.0, self.near, self.far)

        else:
            self.projection = glm.perspective(
                radians(self.__fov),
                self.aspect_ratio,
                self.near,
                self.far
            )