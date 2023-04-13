"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import TYPE_CHECKING, Optional, Union

import glm
import moderngl

from .math import flatten_mat

from .collision import ColliderShape, SphereCollider, MeshCollider, sphere_x_sphere, sphere_x_mesh

if TYPE_CHECKING:
    from .engine import Engine
    from .model import Model
    from .camera import Camera
    from .light import BasicLight


class Entity:
    """
    Base class for all entities in a scene.
    """

    def __init__(self,
            engine: "Engine",
            position: Union[tuple[float, float, float], glm.vec3] = (0.0, 0.0, 0.0),
            rotation: Union[tuple[float, float, float], glm.vec3] = (0.0, 0.0, 0.0),
            scale: Union[tuple[float, float, float], glm.vec3] = (1.0, 1.0, 1.0),
            model: Optional["Model"] = None
            ):
        self.engine = engine
        self.position = glm.vec3(position)
        self.rotation = glm.vec3(rotation)
        self.scale = glm.vec3(scale)
        self.model = model
        self.collider = None

    def set_collider(self, collider_shape: ColliderShape, **kwargs):
        if collider_shape == ColliderShape.SPHERE:
            self.collider = SphereCollider(self, kwargs["radius"])

        if collider_shape == ColliderShape.MESH:
            self.collider = MeshCollider(self, kwargs["mesh"])

    def collide(self, other: "Entity") -> bool:
        # Early out if either entity doesn't have a collider
        if self.collider is None or other.collider is None: return

        # Sphere x Sphere
        if self.collider.shape == ColliderShape.SPHERE and other.collider.shape == ColliderShape.SPHERE:
            return sphere_x_sphere(self.collider, other.collider)
        
        # Sphere x Mesh
        elif self.collider.shape == ColliderShape.SPHERE and other.collider.shape == ColliderShape.MESH:
            return sphere_x_mesh(self.collider, other.collider)

    def update(self, camera: "Camera", light: "BasicLight"):
        if self.model is not None:
            # Create rotation matrix from euler angles
            rotation = glm.rotate(          self.rotation.x, glm.vec3(1.0, 0.0, 0.0))
            rotation = glm.rotate(rotation, self.rotation.y, glm.vec3(0.0, 1.0, 0.0))
            rotation = glm.rotate(rotation, self.rotation.z, glm.vec3(0.0, 0.0, 1.0))

            # Create translation matrix
            translation = glm.translate(self.position)

            # Create scale matrix
            scale = glm.scale(self.scale)

            # Model, projection and view matrices
            model = translation * rotation * scale
            projection = camera.projection
            view = camera.get_view_matrix()

            self.model.update(model, projection, view, camera, light)