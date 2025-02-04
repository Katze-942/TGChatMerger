from enum import Enum

class BetterEnum(Enum):
    """https://stackoverflow.com/questions/6060635/convert-enum-to-int-in-python"""
    def __new__(cls, value):
        level = object.__new__(cls)
        level._value_ = value
        return level

    def __int__(self):
        return self.value
