from typing import TypeVar, Any
import pytest
from YYdlp_GUI.state import RedundancyError, EssentialError, State, ReactiveState

# state.State tests

class TestState:
    def bind_assert_value(value):
        assert value == self.value_now

    def bind_called_value(value):
        self.called_value = value

    def __init__():
        pass

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
    def test_normal(value0,value1):
        state = State(value0)
        self.value_now = value0
        assert state.get() == value0
        state.bind(self.bind_assert_value,self.bind_called_value)
        self.value_now = value1
        state.set(value1)
        assert state.get() == value1
        assert self.called_value == value1

    @pytest.mark.parametrize(
    ("value1"),
    [0, "init", (), [], {}, set()],
    )
    def test_without_args(value1):
        state = State()
        self.value_now = None
        assert state.get() is None
        state.bind(self.bind_assert_value,self.bind_called_value)
        state.set(value1)
        assert state.get() == value1
        assert self.called_value == value1

    def test_state_redudancy_bind():
        state = State()
        self.value_now = None
        state.bind(self.bind_assert_value,self.bind_called_value)
        with pytest.raises(RedundancyError) as error:
            state.bind(self.bind_assert_value)
        assert error.value.target[0].__name__ == "bind_assert_value"
        with pytest.raises(RedundancyError) as error2:
            state.bind(self.bind_called_value, self.bind_assert_value)
        assert error2.value.target[0].__name__ == "bind_called_value"
        assert error2.value.target[1].__name__ == "bind_assert_value"

# state.ReactiveState tests
class TestReactiveState:

    def formula_1(self,value0,value1):
        return value0+value1
    
    def bind_assert_value(value):
        assert value == ( self.state0.get() + self.state1.get() )

    def bind_called_value(value):
        self.called_value = value

    def bind_err_nothing():
        pass

    def fixture_1():
        self.state0 = State(0)
        self.state1 = State(100)
        self.rs = ReactiveState(
            formula=self.formula_1,
            reliance_states=(self.state0,self.state1))
        rs.bind(self.bind_assert_value)
        rs.bind(self.bind_called_value)

    def __init__(self):
        pass

    def test_1():
        self.fixture_1()
        rs = self.rs
        state0 = self.state0
        state1 = self.state1
        assert rs.get() = 0+100
        state0.set(1)
        assert rs.get() == 1+100
        assert self.called_value == rs.get()
        state1.set(0)
        assert rs.get() == 1+0
        assert self.called_value == rs.get()

    def test_with_errors_1():
        rs = self.rs
        state0 = self.state0
        state1 = self.state1
        with pytest.raises(RedundancyError) as redudancy_error:
            reactive_state.bind(self.bind_assert_value,self.bind_err_nothing)
        assert redudancy_error.target[0].__name__ == "bind_assert_value"
        with pytest.raises(RedundancyError) as redudancy_error
            reactive_state.bind(self.bind_err_nothing,self.bind_assert_value)
        assert redudancy_error.target[0].__name__ == "bind_err_nothing"
        assert redudancy_error.target[1].__name__ == "bind_assert_value"

class TestStore:

    def __init__():
        pass