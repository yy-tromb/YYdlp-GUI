from typing import TypeVar, Generic, Union, Callable

T = TypeVar('T')

class State(Generic[T]):
    def __init__(self, value: T):
        self.__value = value
        self.__observers: list[Callable] = []

    def get(self):
        return self.__value

    def set(self, new_value: T):
        if self.__value != new_value:
            self.__value = new_value
            for observer in self.__observers:
                observer()

    def bind(self, observer):
        self.__observers.append(observer)
