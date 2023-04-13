"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""


def create_plane_mesh(
        size: float,
        scale_uv_coords: bool = False
        ) -> tuple[list[float], list[float], list[float]]:
    """ Create plane vertices, normals and UV coords. """

    x = size / 2.0
    y = size / 2.0

    vertices = [
        x, y, 0.0,  -x, -y, 0.0,  -x,  y, 0.0,
        x, y, 0.0,   x, -y, 0.0,  -x, -y, 0.0
    ]

    normals = []
    for _ in range(len(vertices)):
        normals.append(0.0)
        normals.append(0.0)
        normals.append(-1.0)

    if not scale_uv_coords: size = 1.0
    uv_coords = [
        size, 0.0,   0.0,  size,
        0.0,  0.0,   size, 0.0,
        size, size,  0.0,  size
    ]

    return  (vertices, normals, uv_coords)


def create_cube_mesh(
        size: float,
        scale_uv_coords: bool = False
        ) -> tuple[list[float], list[float], list[float]]:
    """ Create cube vertices, normals and UV coords. """
    
    vertices = [
         size, -size,  size,  -size, -size,  size,  -size, -size, -size,
        -size,  size, -size,  -size,  size,  size,   size,  size,  size,
        
         size,  size, -size,   size,  size,  size,   size, -size,  size,
         size,  size,  size,  -size,  size,  size,  -size, -size,  size,

        -size, -size,  size,  -size,  size,  size,  -size,  size, -size,
         size, -size, -size,  -size, -size, -size,  -size,  size, -size,

         size, -size, -size,   size, -size,  size,  -size, -size, -size,
         size,  size, -size,  -size,  size, -size,   size,  size,  size,

         size, -size, -size,   size,  size, -size,   size, -size,  size,
         size, -size,  size,   size,  size,  size,  -size, -size,  size,

        -size, -size, -size,  -size, -size,  size,  -size,  size, -size,
         size,  size, -size,   size, -size, -size,  -size,  size, -size
    ]

    normals = [
         0.0, -1.0,  0.0,   0.0, -1.0,  0.0,   0.0, -1.0,  0.0,
         0.0,  1.0,  0.0,   0.0,  1.0,  0.0,   0.0,  1.0,  0.0,

         1.0,  0.0,  0.0,   1.0,  0.0,  0.0,   1.0,  0.0,  0.0,
        -0.0,  0.0,  1.0,  -0.0,  0.0,  1.0,  -0.0,  0.0,  1.0,

        -1.0, -0.0, -0.0,  -1.0, -0.0, -0.0,  -1.0, -0.0, -0.0,
         0.0,  0.0, -1.0,   0.0,  0.0, -1.0,   0.0,  0.0, -1.0,

         0.0, -1.0,  0.0,   0.0, -1.0,  0.0,   0.0, -1.0,  0.0,
         0.0,  1.0,  0.0,   0.0,  1.0,  0.0,   0.0,  1.0,  0.0,

         1.0,  0.0,  0.0,   1.0,  0.0,  0.0,   1.0,  0.0,  0.0,
        -0.0,  0.0,  1.0,  -0.0,  0.0,  1.0,  -0.0,  0.0,  1.0,

        -1.0, -0.0, -0.0,  -1.0, -0.0, -0.0,  -1.0, -0.0, -0.0,
         0.0,  0.0, -1.0,   0.0,  0.0, -1.0,   0.0,  0.0, -1.0
    ]

    if not scale_uv_coords: size = 1.0
    s1 = size / 3.0
    s2 = 2.0 * size / 3.0
    uv = [
        size, s1,  size, s2, 
        s2,  s2,   size, s1,
        s2,  s1,   s2,  0.0,
        0.0, s1,   0.0, 0.0,
        s1,  0.0,  s1,  0.0,
        s2,  0.0,  s2,  s1,
        s1,  size,  0.0, size,
        0.0, s2,   s1,  s1,
        s1,  s2,   0.0, s2,
        s2,  s1,   size, s1,
        s2,  s2,   size, 0.0,
        size, s1,  s2,  0.0,
        s1,  s1,   0.0, s1,
        s1,  0.0,  s1,  s1,
        s1,  0.0,  s2,  s1,
        s1,  s2,   s1,  size,
        0.0, s2,   0.0, s1,
        s1,  s1,   0.0, s2
    ]

    return (vertices, normals, uv)