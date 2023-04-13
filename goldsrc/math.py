"""

    GoldSrc Python
    MIT © Kadir Aksoy
    https://github.com/kadir014/goldsrc-python

"""

from typing import Union, overload

from math import sqrt

import glm


def flatten_mat(
        matrix: Union[
            glm.mat2,
            glm.mat3,
            glm.mat4,
            glm.mat2x2,
            glm.mat3x3,
            glm.mat4x4,
            glm.mat2x3,
            glm.mat3x2,
            glm.mat2x4,
            glm.mat4x2,
            glm.mat3x4,
            glm.mat4x3
        ]
        ) -> tuple:
    """ Flatten any GLM matrix into 1D tuple. """
    return tuple(sum(matrix.to_tuple(), ()))


def flatten_2dlist(list2d: list) -> list:
    """ Flatten 2D list into 1D tuple. """
    return sum(list2d, [])


class Vector3:
    """
    3D vector type.
    """

    @overload
    def __init__(self): ...
    
    @overload
    def __init__(self, x: float): ...

    @overload
    def __init__(self, x: float, y: float): ...

    @overload
    def __init__(self, x: float, y: float, z: float): ...

    @overload
    def __init__(self, vector_tuple: tuple[float, float, float]): ...

    @overload
    def __init__(self, vector: "Vector3"): ...

    def __init__(self, *args):
        self.x, self.y, self.z = 0.0, 0.0, 0.0
        
        if len(args) == 1:
            # Vector3(x)
            if isinstance(args[0], (float, int)):
                self.x, self.y, self.z = args[0], args[0], args[0]

            elif isinstance(args[0], (tuple, list)):
                self.x, self.y, self.z = args[0]

            elif isinstance(args[0], Vector3):
                self.x, self.y, self.z = args[0].x, args[0].y, args[0].z

            else:
                raise TypeError("single argument must be float, int, tuple or Vector3.")

        # Vector3(x, y)
        elif len(args) == 2:
            if not isinstance(args[0], (float, int)) or \
               not isinstance(args[1], (float, int)):
                raise TypeError("arguments must be float or int.")
            
            self.x, self.y = args[0], args[1]

        # Vector3(x, y, z)
        elif len(args) == 3:
            if not isinstance(args[0], (float, int)) or \
               not isinstance(args[1], (float, int)) or \
               not isinstance(args[1], (float, int)):
                raise TypeError("arguments must be float or int.")
                
            self.x, self.y, self.z = args

    def __repr__(self):
        return f"<Vector3({self.x}, {self.y}, {self.z})>"
    
    def __add__(self, other: Union["Vector3", Union[float, int]]):
        # Vector3 + Vector3
        if isinstance(other, Vector3):
            return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
        
        # Vector3 + Scalar
        elif isinstance(other, (float, int)):
            return Vector3(self.x + other, self.y + other, self.z + other)
        
        else:
            raise TypeError(f"unsupported operand type(s) for +: 'Vector3' and '{type(other).__name__}'")
        
    def __sub__(self, other: Union["Vector3", Union[float, int]]):
        # Vector3 - Vector3
        if isinstance(other, Vector3):
            return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
        
        # Vector3 - Scalar
        elif isinstance(other, (float, int)):
            return Vector3(self.x - other, self.y - other, self.z - other)
        
        else:
            raise TypeError(f"unsupported operand type(s) for -: 'Vector3' and '{type(other).__name__}'")
        
    def __mul__(self, other: Union["Vector3", Union[float, int]]):
        # Vector3 * Vector3
        if isinstance(other, Vector3):
            return Vector3(self.x * other.x, self.y * other.y, self.z * other.z)
        
        # Vector3 * Scalar
        elif isinstance(other, (float, int)):
            return Vector3(self.x * other, self.y * other, self.z * other)
        
        else:
            raise TypeError(f"unsupported operand type(s) for *: 'Vector3' and '{type(other).__name__}'")
        
    def __truediv__(self, other: Union["Vector3", Union[float, int]]):
        # Vector3 / Vector3
        if isinstance(other, Vector3):
            return Vector3(self.x / other.x, self.y / other.y, self.z / other.z)
        
        # Vector3 / Scalar
        elif isinstance(other, (float, int)):
            return Vector3(self.x / other, self.y / other, self.z / other)
        
        else:
            raise TypeError(f"unsupported operand type(s) for /: 'Vector3' and '{type(other).__name__}'")
        
    def __floordiv__(self, other: Union["Vector3", Union[float, int]]):
        # Vector3 // Vector3
        if isinstance(other, Vector3):
            return Vector3(self.x // other.x, self.y // other.y, self.z // other.z)
        
        # Vector3 // Scalar
        elif isinstance(other, (float, int)):
            return Vector3(self.x // other, self.y // other, self.z // other)
        
        else:
            raise TypeError(f"unsupported operand type(s) for //: 'Vector3' and '{type(other).__name__}'")
        
    def __neg__(self):
        # -Vector3
        return Vector3(-self.x, -self.y, -self.z)
    
    def __abs__(self):
        # abs(Vector3)
        return Vector3(abs(self.x), abs(self.y), abs(self.z))
    
    def to_tuple(self) -> tuple[float, float, float]:
        """ Convert vector to tuple. """
        return (self.x, self.y, self.z)
    
    def len2(self) -> float:
        """ Calculate squared length (magnitude) of the vector. """
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def len(self) -> float:
        """ Calculate length (magnitude) of the vector. """
        return sqrt(self.len2())
    
    def dot(self, vector: "Vector3") -> float:
        """ Calculate dot product of two vectors. """
        return 

    #@property
    #def xy(self): return Vector2(self.x, self.y)
    
    @property
    def xzy(self) -> "Vector3": return Vector3(self.x, self.z, self.y)

    @property
    def yxz(self) -> "Vector3": return Vector3(self.y, self.x, self.z)

    @property
    def yzx(self) -> "Vector3": return Vector3(self.y, self.z, self.x)

    @property
    def zyx(self) -> "Vector3": return Vector3(self.z, self.y, self.x)

    @property
    def zxy(self) -> "Vector3": return Vector3(self.z, self.x, self.y)