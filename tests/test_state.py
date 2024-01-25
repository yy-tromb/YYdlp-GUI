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
    assert error.value.target[0].__name__ == "bind_1"
    with pytest.raises(RedundancyError) as error2:
        state.bind(bind_2, bind_1)
    assert error2.value.target[0].__name__ == "bind_2"
    assert error2.value.target[1].__name__ == "bind_1"

# state.ReactiveState tests
def formula(value0,value1):
    return value0+value1

@pytest.fixture(scope="function",autouse=True)
def reactive_state_set():
    state0 = State(0)
    state1 = State(100)
    reactive_state = ReactiveState(
        formula=formula,
        reliance_states=(state0,state1))
    return (reactive_state,state0,state1)

def test_reactive_state_normal(reactive_state_set):
    reactive_state = reactive_state_set[0]
    state0 = reactive_state_set[1]
    state1 = reactive_state_set[2]
    reactive_state.bind(lambda value: assert value == state0.get() + state1.get())
    reactive_state_bind_called = reactive_state.get()
    reactive_state.bind(lambda value: reactive_state_bind_called = value)
    assert reactive_state.get() == 0+100
    state0.set(1)
    assert reactive_state.get() == 1+100
    assert reactive_state_bind_called == reactive_state.get()
    state1.set(0)
    assert reactive_state.get() == 1+0
    assert reactive_state_bind_called == reactive_state.get()
    
def test_reactive_state_error(reactive_state_set):
    reactive_state = reactive_state_set[0]
    state0 = reactive_state_set[1]
    state1 = reactive_state_set[2]
    called_value = reactive_state.get()
    bind_1 = lambda value: called_value = value
    bind_2 = lambda v: v
    reactive_state.bind(bind_1)
    with pytest.raises(RedundancyError) as redudancy_error:
        reactive_state.bind(bind_1,bind_2)
    assert redudancy_error.target[0].__name__ == "bind_1"
    with pytest.raises(RedundancyError) as redudancy_error
        reactive_state.bind(bind_2,bind_1)
    assert redudancy_error.target[0].__name__ == "bind_2"
    assert redudancy_error.target[1].__name__ == "bind_1"