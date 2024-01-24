from typing import TypeVar, Any
import pytest
from YYdlp_GUI.state import RedundancyError, EssentialError, State, ReactiveState

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
    assert state.get() == value1

@pytest.mark.parametrize(
    ("value1"),
    [0, "init", (), [], {}, set()],
)
def test_state_without_arg(value1: T) -> None:
    state = State()
    assert state.get() is None
    state.bind(bind_1, bind_2)
    state.set(value1)
    assert bind_1_value[0] == value1
    assert bind_2_value[0] == value1
    assert state.get() == value1

def test_state_redudancy_bind():
    state = State()
    state.bind(bind_1, bind_2)
    state.set(0)
    assert bind_1_value[0] == 0
    assert bind_2_value[0] == 0
    assert state.get() == 0
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

# state.ReactiveState tests

@pytest.fixture(scope="function",autouse=True)
def reactive_state_set():
    state0 = State(0)
    state1 = State(100)
    def formula(value0,value1):
        return value0+value1
    reactive_state = ReactiveState(
        formula=formula,
        reliance_states=(state0,state1))
    return (reactive_state,state0,state1)

def test_reactive_state_normal(reactive_state_set):
    reactive_state = reactive_state_set[0]
    state0 = reactive_state_set[1]
    state1 = reactive_state_set[2]
    assert reactive_state.get() == 0+100
    state0.set(1)
    assert reactive_state.get() == 1+100