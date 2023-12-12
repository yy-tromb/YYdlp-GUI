from typing import TypeVar, Any
import pytest
from YYdlp_GUI.state import State, RedundancyError, EssentialError

T = TypeVar("T")

# state.State tests

bind_1_value: list[T] = [None]
bind_2_value: list[T] = [None]


def bind_1(value: T) -> None:
    print(f"bind_1 : {value}")
    bind_1_value[0] = value


def bind_2(value: T) -> None:
    print(f"bind_2 : {value}")
    bind_2_value[0] = value


@pytest.mark.parametrize(
    ("value0", "value1"),
    [
        (None, 0),
        (0, 2),
        ("init", "2nd"),
        ("init", None),
        ((), (0, "", ())),
        ([], [0, 1, 2]),
        ({}, {"now": "second"}),
    ],
)
def test_state_normal(value0: T, value1: T) -> None:
    state = State(value0)
    assert state.get() == value0
    state.bind(bind_1, bind_2)
    state.set(value1)
    assert bind_1_value[0] == value1
    assert bind_2_value[0] == value1
    with pytest.raises(RedundancyError) as error:
        state.bind(bind_1)
    assert error.value._target[0].__name__ == "bind_1"
    assert error.value._message == "redudancy observer was given"
    with pytest.raises(RedundancyError) as error2:
        state.bind(bind_2, bind_1)
    assert (
        error2.value._target[0].__name__ == "bind_2"
        and error2.value._target[1].__name__ == "bind_1"
    )
    assert error2.value._message == "redudancy observer was given"

@pytest.mark.parametrize(
    ("value0","value1"),
    [
        (0,""),
        ("init",256),
    ],
)
def test_state_miss_type(value0: Any,value1: Any):
    state = State(value0)