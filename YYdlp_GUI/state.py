from typing import TypeVar, Generic, Union, Callable

T = TypeVar('T')

class State(Generic[T]):
    def __init__(self, value: T):
        self._value = value
        self._observers: list[Callable] = []

    def get(self):
        return self._value

    def set(self, new_value: T):
        if self._value != new_value:
            self._value = new_value
            for observer in self._observers:
                observer()

    def bind(self, observer):
        self._observers.append(observer)
