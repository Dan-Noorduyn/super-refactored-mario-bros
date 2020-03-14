from utils.physics import Vector2D

class Entity():

    ## @brief Intitializes an entity with a position.
    # @param x Initial x position of the entity.
    # @param y Initial y position of the entity.
    # @exception TypeError Arguments are not of type float.
    def __init__(self, x: float, y: float):
        try:
            assert(isinstance(x, float))
            assert(isinstance(y, float))
        except AssertionError as e:
            raise(TypeError("Arguments are not of type float."))
    
        self.__pos: Vector2D = Vector2D(x, y)
        self.__vel: Vector2D = Vector2D(0, 0)
        self.__acc: Vector2D = Vector2D(0, 0)

    ## @brief Gets the position of the entity.
    # @returns The position of the entity.
    def get_pos(self) -> Vector2D:
        return Vector2D(self.__pos.get_x(), self.__pos.get_y())

    ## @brief 
    def update_pos(self, v: Vector2D) -> None:
        self.__pos += v

    def set_pos(self, x: float, y: float) -> None:
        self.__pos = Vector2D(x, y)

    def get_vel(self) -> Vector2D:
        return Vector2D(self.__vel.get_x(), self.__vel.get_y())

    def update_vel(self, v: Vector2D) -> None:
        self.__vel += v

    def set_vel(self, vx: float, vy: float) -> None:
        self.__vel = Vector2D(vx, vy)

    def get_acc(self) -> Vector2D:
        return Vector2D(self.__vel.get_x(), self.__vel.get_y())

    def update_acc(self, v: Vector2D) -> None:
        self.__acc += v

    def set_acc(self, ax: float, ay: float) -> None:
        self.__acc = Vector2D(ax, ay)

    def update(self) -> None:
        self.__vel += Vector2D(self.__acc.get_x(), self.__acc.get_y())
        self.__pos += Vector2D(self.__vel.get_y(), self.__vel.get_y())

