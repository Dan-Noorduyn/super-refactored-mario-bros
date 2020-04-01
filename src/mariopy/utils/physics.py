"""
    @brief
"""

from math import sqrt

class Vector2D():
    def __init__(self, x: float, y: float):
        self.__x: float = x
        self.__y: float = y

    def get_x(self) -> float:
        return self.__x

    def get_y(self) ->  float:
        return self.__y

    def add(self, v: "Vector2D") -> None:
        self.__x += v.get_x()
        self.__y += v.get_y()

    def set_x(self, x: float) -> None:
        self.__x = x

    def set_y(self, y: float) -> None:
        self.__y = y

    def mag(self) -> float:
        return sqrt(self.__x * self.__x + self.__y * self.__y)

    def __repr__(self) -> str:
        return f"Vector2D({self.__x}, {self.__y})"

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, v: "Vector2D") -> bool:
        if self.__x == v.get_x() and self.__y == v.get_y():
            return True
        return False

    def __lt__(self, v: "Vector2D") -> bool:
        return self.mag() < v.mag()

    def __add__(self, v: "Vector2D") -> "Vector2D":
        return Vector2D(self.__x + v.get_x(), self.__y + v.get_y())

    def __sub__(self, v: "Vector2D") -> "Vector2D":
        return Vector2D(self.__x - v.get_x(), self.__y - v.get_y())
