"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from math import radians, cos, sin, pi

import glm

from goldsrc import Scene, Engine, Entity, Model, Camera, BasicLight, ColliderShape
import goldsrc.objparser
from goldsrc.path import source_path


class CollisionTest(Scene):
    def __init__(self, engine: Engine):
        super().__init__(engine)

        self.engine.enable_virtual_mouse()

        self.light = BasicLight(
            glm.vec3(0.0, 5.0, 0.0),
            glm.vec3(1.0, 1.0, 1.0),
            ambient_intensity=0.2,
        )

        self.camera = Camera(self.engine.aspect_ratio)

        self.position = glm.vec3(0.0)
        self.velocity = glm.vec3(0.0)

        sphere_obj = goldsrc.objparser.parse(source_path("assets", "models", "sphere.obj"))

        sphere_model1 = Model(
            self.engine,
            sphere_obj.vertices,
            sphere_obj.normals,
            sphere_obj.uv_coords,
            program_name="flat",
            color=glm.vec4(1.0, 0.0, 0.0, 1.0)
        )
        self.sphere1 = Entity(
            self.engine,
            position=glm.vec3(2.0, 0.0, 0.0),
            model=sphere_model1
        )
        self.sphere1.set_collider(ColliderShape.SPHERE, radius=1.0)
        self.add_entity(self.sphere1)

        sphere_model2 = Model(
            self.engine,
            sphere_obj.vertices,
            sphere_obj.normals,
            sphere_obj.uv_coords,
            program_name="flat",
            color=glm.vec4(1.0, 0.0, 0.0, 1.0)
        )
        self.sphere2 = Entity(
            self.engine,
            position=glm.vec3(-2.0, 0.0, 0.0),
            model=sphere_model2
        )
        self.sphere2.set_collider(ColliderShape.SPHERE, radius=1.0)
        #self.add_entity(self.sphere2)

        plane_model = Model.from_plane(
            self.engine,
            25.0,
            color=glm.vec4(0.0, 0.6, 1.0, 1.0),
            program_name="unlitflat"
        )
        self.plane = Entity(
            self.engine,
            glm.vec3(0.0, 0.0, 0.0),
            model=plane_model
        )
        self.plane.set_collider(ColliderShape.MESH, mesh=plane_model.vertices)
        self.add_entity(self.plane)
        #self.plane.rotation.y -= pi / 2
        
    def update(self):
        if self.engine.input.key_pressed("escape"):
            self.engine.stop()

        offset = self.engine.mouse_rel.copy()
        offset *= 0.15

        self.camera.yaw += radians(offset.x)
        self.camera.pitch -= radians(offset.y)

        speed = 0.5 * self.engine.dt

        if self.engine.input.key_held("w"):
            self.velocity.x += cos(self.camera.yaw) * speed
            self.velocity.z += sin(self.camera.yaw) * speed

        if self.engine.input.key_held("s"):
            self.velocity.x -= cos(self.camera.yaw) * speed
            self.velocity.z -= sin(self.camera.yaw) * speed

        if self.engine.input.key_held("a"):
            self.velocity.x -= cos(self.camera.yaw + pi/2) * speed
            self.velocity.z -= sin(self.camera.yaw + pi/2) * speed

        if self.engine.input.key_held("d"):
            self.velocity.x += cos(self.camera.yaw + pi/2) * speed
            self.velocity.z += sin(self.camera.yaw + pi/2) * speed

        if self.engine.input.key_held("space"):
            self.velocity.y += speed

        if self.engine.input.key_held("lshift"):
            self.velocity.y -= speed

        speed = 3.2 * self.engine.dt

        if self.engine.input.key_held("up"):
            self.sphere1.position.x -= speed

        if self.engine.input.key_held("down"):
            self.sphere1.position.x += speed

        if self.engine.input.key_held("left"):
            self.sphere1.position.z += speed

        if self.engine.input.key_held("right"):
            self.sphere1.position.z -= speed

        if self.engine.input.key_held("q"):
            self.sphere1.position.y += speed

        if self.engine.input.key_held("e"):
            self.sphere1.position.y -= speed

        # Integrate velocities
        self.velocity *= 0.9
        self.position += self.velocity
        self.camera.position = self.position
        self.light.position = self.position


        if self.sphere1.collide(self.plane):
            self.sphere1.model.color = glm.vec4(0.0, 1.0, 0.0, 1.0)
        else:
            self.sphere1.model.color = glm.vec4(1.0, 0.0, 0.0, 1.0)