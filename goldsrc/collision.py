"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""


from typing import TYPE_CHECKING

from dataclasses import dataclass
from enum import Enum

import glm

from .model import Model

if TYPE_CHECKING:
    from .entity import Entity


class ColliderShape(Enum):
    SPHERE = 0
    CAPSULE = 1
    AABB = 2
    MESH = 3


@dataclass
class SphereCollider:
    """
    Sphere collider shape.
    """
    
    entity: "Entity"
    radius: float
    shape: ColliderShape = ColliderShape.SPHERE


@dataclass
class CapsuleCollider:
    """
    Capsule collider shape.
    """


@dataclass
class MeshCollider:
    """
    Mesh collider shape.
    """

    entity: "Entity"
    mesh: list[float]
    shape: ColliderShape = ColliderShape.MESH


def sphere_x_sphere(a: SphereCollider, b: SphereCollider) -> bool:
    """ Sphere x Sphere collision. """
    dist = glm.distance2(b.entity.position, a.entity.position)
    radii = (b.radius + a.radius) ** 2

    return dist < radii


def closest_point_on_line(a: glm.vec3, b: glm.vec3, point: glm.vec3):
    ab = b - a
    t = glm.dot(point - a, ab) / glm.dot(ab, ab)
    return a + min(max(t, 0), 1) * ab


def scale(u, c):
    return [c * ui for ui in u]


def project_onto_plane(v1, v2, v3):
    # Calculate the normal vector of the plane
    normal = glm.cross(v2 - v1, v3 - v1)
    normal /= glm.normalize(normal)

    # Project the vertices onto the plane
    p1 = v1 - normal * glm.dot(v1, normal)
    p2 = v2 - normal * glm.dot(v2, normal)
    p3 = v3 - normal * glm.dot(v3, normal)

    return p1, p2, p3

def barycentric_coords(p, triangle):
    v0, v1, v2 = triangle
    # Calculate the area of the main triangle
    area = glm.normalize(glm.cross(v1 - v0, v2 - v0)) / 2.0
    # Calculate the areas of the sub-triangles formed by the point and each vertex
    area0 = glm.normalize(glm.cross(v1 - p, v2 - p)) / 2.0
    area1 = glm.normalize(glm.cross(v2 - p, v0 - p)) / 2.0
    area2 = glm.normalize(glm.cross(v0 - p, v1 - p)) / 2.0
    # Calculate the barycentric coordinates using the ratios of the sub-triangle areas
    u = area0 / area
    v = area1 / area
    w = area2 / area
    return u, v, w

def sphere_segment_intersection(center, radius, p1, p2):
    # Calculate the direction and length of the line segment
    direction = p2 - p1
    length = glm.normalize(direction)

    # Calculate the vector from the center of the sphere to the start point of the line segment
    v = center - p1

    # Calculate the projection of v onto the direction of the line segment
    projection = glm.dot(v, direction) / length

    # Calculate the distance between the center of the sphere and the line segment
    distance = glm.length(glm.normalize(v - projection * direction / length))

    # If the distance is less than the radius of the sphere, they intersect
    return distance < radius


def sphere_x_triangle(
        sphere: SphereCollider,
        triangle: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
        ) -> bool:
    """ Sphere x Triangle collision. """

    center = sphere.entity.position
    radius = sphere.radius
    vertices = (glm.vec3(triangle[0]), glm.vec3(triangle[1]), glm.vec3(triangle[2]))

    v0, v1, v2 = vertices
    # Calculate the barycentric coordinates of the sphere center
    u, v, w = barycentric_coords(center, vertices)
    # Check if the sphere center is inside the triangle
    if (u[0] >= 0) and (u[1] >= 0) and (u[2] >= 0) and (u[0] + u[1] + u[2] <= 1):
        return True
    # Check if the sphere intersects any of the triangle edges
    edges = ((v0, v1), (v1, v2), (v2, v0))
    for e1, e2 in edges:
        if sphere_segment_intersection(center, radius, e1, e2):
            return True
    # If we get here, the sphere does not intersect the triangle
    return False

    # # Check if the sphere intersects the triangle in the x-y plane
    # # by checking if the projection of the center onto the plane of
    # # the triangle is inside the triangle
    # x, y, z = center
    # p1, p2, p3 = project_onto_plane(v1, v2, v3)
    # b1, b2, b3 = barycentric_coords(x, y, z, p1, p2, p3)
    # if all(l >= 0 for l in (b1, b2, b3)):
    #     return True

    # # Check if the sphere intersects the triangle in the z direction
    # min_z = min(v1[2], v2[2], v3[2])
    # max_z = max(v1[2], v2[2], v3[2])
    # if z + radius < min_z or z - radius > max_z:
    #     return False

    # # Check if the sphere intersects the triangle in one of the three edges
    # if any(sphere_segment_intersection(center, radius, v1, v2),
    #        sphere_segment_intersection(center, radius, v2, v3),
    #        sphere_segment_intersection(center, radius, v3, v1)):
    #     return True

    # # Check if the sphere is inside the triangle
    # if all(l >= 0 for l in (b1, b2, b3)):
    #     return True

    # return False


    # # Check if any vertex is inside the sphere
    # for v in vertices:
    #     if glm.distance(center, v) <= radius:
    #         return True

    # # Check if the sphere intersects any of the triangle edges
    # for i in range(3):
    #     j = (i + 1) % 3
    #     edge = vertices[j] - vertices[i]
    #     sphere_to_edge = glm.clamp(glm.dot(center - vertices[i], edge) / glm.dot(edge, edge), 0.0, 1.0)
    #     #sphere_to_edge = ((center - vertices[i]).dot(edge) / edge.dot(edge)).clamp(0, 1)
    #     closest_point = vertices[i] + sphere_to_edge * edge
    #     if glm.distance(center, closest_point) <= radius:
    #         return True

    # # Check if the sphere is inside the triangle
    # x1, y1, z1 = vertices[0]
    # x2, y2, z2 = vertices[1]
    # x3, y3, z3 = vertices[2]
    # x, y, z = center

    # # Compute barycentric coordinates of the sphere center with respect to the triangle
    # lambda1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3) + (z3 - z2) * (z - z3)) / ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3) + (z3 - z2) * (z1 - z3))
    # lambda2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3) + (z1 - z3) * (z - z3)) / ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3) + (z3 - z2) * (z1 - z3))
    # lambda3 = 1 - lambda1 - lambda2

    # if 0 <= lambda1 <= 1 and 0 <= lambda2 <= 1 and 0 <= lambda3 <= 1:
    #     return True

    # return False


    # # Check if any vertex is inside the sphere
    # for v in vertices:
    #     if glm.distance(center, v) <= radius:
    #         return True

    # # Check if the sphere intersects any of the triangle edges
    # for i in range(3):
    #     j = (i + 1) % 3
    #     edge = vertices[j] - vertices[i]
    #     sphere_to_edge = glm.clamp(glm.dot(center - vertices[i], edge) / glm.dot(edge, edge), 0.0, 1.0)
    #     #sphere_to_edge = ((center - vertices[i]).dot(edge) / edge.dot(edge)).clamp(0, 1)
    #     closest_point = vertices[i] + sphere_to_edge * edge
    #     if glm.distance(center, closest_point) <= radius:
    #         return True

    # # Check if the sphere intersects the triangle face
    # normal = glm.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])
    # #normal = (vertices[1] - vertices[0]).cross(vertices[2] - vertices[0])
    # d = glm.dot(-normal, vertices[0])
    # #d = -normal.dot(vertices[0])
    # dist_to_plane = glm.dot(normal, center) + d
    # #dist_to_plane = normal.dot(center) + d
    # if abs(dist_to_plane) <= radius:
    #     # Check if the closest point on the plane is inside the triangle
    #     closest_point = center - dist_to_plane * normal
    #     bary_coords = [0.0, 0.0, 0.0]
    #     for i in range(3):
    #         j, k = (i + 1) % 3, (i + 2) % 3
    #         edge1 = vertices[j] - closest_point
    #         edge2 = vertices[k] - closest_point
    #         normal = glm.cross(edge1, edge2)
    #         if glm.dot(normal, vertices[i] - closest_point) > 0:
    #             break
    #         bary_coords[i] = glm.length(normal)
    #     else:
    #         if sum(bary_coords) <= glm.length(glm.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])):
    #             return True

    # return False


    # center = sphere.entity.position

    # triangle = (glm.vec3(triangle[0]), glm.vec3(triangle[1]), glm.vec3(triangle[2]))
    # v0, v1, v2 = triangle
    
    # d0 = glm.distance(v0, center)
    # d1 = glm.distance(v1, center)
    # d2 = glm.distance(v2, center)

    # d = float("inf")
    # v = None
    # if d0 < d:
    #     d = d0
    #     v = v0
    # if d1 < d:
    #     d = d1
    #     v = v1
    # if d2 < d:
    #     d = d2
    #     v = v2

    # m = glm.length(v - center)
    # test1 = m <= sphere.radius


    # c0 = closest_point_on_line(v0, v1, center)
    # c1 = closest_point_on_line(v0, v2, center)
    # c2 = closest_point_on_line(v1, v2, center)

    # d0 = glm.distance(c0, center)
    # d1 = glm.distance(c1, center)
    # d2 = glm.distance(c2, center)

    # d = float("inf")
    # v = None
    # if d0 < d:
    #     d = d0
    #     v = v0
    # if d1 < d:
    #     d = d1
    #     v = v1
    # if d2 < d:
    #     d = d2
    #     v = v2

    # m = glm.length(v - center)
    # test2 = m <= sphere.radius

    # return test1 or test2



def sphere_x_mesh(sphere: SphereCollider, mesh: MeshCollider) -> bool:
    """ Sphere x Mesh collision. """

    v0 = mesh.mesh[0:3]
    v1 = mesh.mesh[3:6]
    v2 = mesh.mesh[6:9]
    triangle1 = (v0, v1, v2)
    triangle2 = mesh.mesh[3:]

    return sphere_x_triangle(sphere, triangle1)


class AABB:
    """
    Axis-aligned bounding box shape.
    """

    def __init__(self, position: glm.vec3, size: glm.vec3):
        self.size = size
        self.update(position)

    def update(self, position: glm.vec3):
        """ Update the bounding box values. """

        s = self.size / 2.0

        self.min_x = position.x - s.x
        self.max_x = position.x + s.x
        self.min_y = position.y - s.y
        self.max_y = position.y + s.y
        self.min_z = position.z - s.z
        self.max_z = position.z + s.z


class Collider:
    def __init__(self, model: Model, size: glm.vec3):
        self.model = model
        self.size = size * 2.0
        self.position = glm.vec3(0.0, 0.0, 0.0)

    def collide(self, collider: "Collider"):
        if self.model is not None:
            a = self.model.position
        else:
            a = self.position

        if collider.model is not None:
            b = collider.model.position
        else:
            b = collider.position

        sa = self.size / 2.0
        sb = collider.size / 2.0

        a_min_x = a.x - sa.x
        a_max_x = a.x + sa.x
        a_min_y = a.y - sa.y
        a_max_y = a.y + sa.y
        a_min_z = a.z - sa.z
        a_max_z = a.z + sa.z
        b_min_x = b.x - sb.x
        b_max_x = b.x + sb.x
        b_min_y = b.y - sb.y
        b_max_y = b.y + sb.y
        b_min_z = b.z - sb.z
        b_max_z = b.z + sb.z

        return not (a_max_x <= b_min_x or b_max_x <= a_min_x or \
                    a_max_y <= b_min_y or b_max_y <= a_min_y or \
                    a_max_z <= b_min_z or b_max_z <= a_min_z)

    