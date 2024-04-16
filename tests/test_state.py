from typing import Any # noqa F401
import pytest
from YYdlp_GUI.state import RedundancyError, EssentialError, State, ReactiveState # noqa F401

# state.State tests

class TestState:
    def bind_assert_value(self,value):
        assert value == self.value_now

    def bind_called_value(self,value):
        self.called_value = value

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
    def test_normal(self,value0,value1):
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
    def test_without_args(self,value1):
        state = State()
        self.value_now = None
        assert state.get() is None
        state.bind(self.bind_assert_value,self.bind_called_value)
        self.value_now = value1
        state.set(value1)
        assert state.get() == value1
        assert self.called_value == value1

    def test_state_redudancy_bind(self):
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

    def bind_assert_value(self,value):
        assert value == ( self.state0.get() + self.state1.get() )

    def bind_called_value(self,value):
        self.called_value = value

    def bind_err_nothing(self):
        pass

    def fixture_1(self):
        self.state0 = State(0)
        self.state1 = State(100)
        self.rs = ReactiveState(
            formula=self.formula_1,
            reliance_states=(self.state0,self.state1))
        self.rs.bind(self.bind_assert_value)
        self.rs.bind(self.bind_called_value)

    def test_1(self):
        self.fixture_1()
        rs = self.rs
        state0 = self.state0
        state1 = self.state1
        assert rs.get() == 0+100
        state0.set(1)
        assert rs.get() == 1+100
        assert self.called_value == rs.get()
        state1.set(0)
        assert rs.get() == 1+0
        assert self.called_value == rs.get()

    def test_with_errors_1(self):
        self.fixture_1()
        rs = self.rs
        with pytest.raises(RedundancyError) as exc_info:
            rs.bind(self.bind_assert_value,self.bind_err_nothing)
            redudancy_error = exc_info._excinfo[1]
            assert redudancy_error.target[0].__name__ == "bind_assert_value"
        with pytest.raises(RedundancyError) as exc_info:
            rs.bind(self.bind_err_nothing,self.bind_assert_value)
            redudancy_error = exc_info._excinfo[1]
            assert redudancy_error.target[0].__name__ == "bind_err_nothing"
            assert redudancy_error.target[1].__name__ == "bind_assert_value"

class TestStore:

    def formula_1(self,value):
        return list(range(value))

    def formula_2(self,new_str):
        self.__last_formula_2 = self.__last_formula_2 + new_str
        return self.__last_formula_2

    def init(self):
        self.__last_formula_2 = ""
        self.state_1 = State(0)
        self.state_2 = State("inited")
        self.rct_state = ReactiveState(
            formula=lambda num,_str:f"{num}:{_str}\n",
            reliance_states=(self.state_1,self.state_2))
        assert self.rct_state.get() == "0:inited"
    
    def test_init(self):
        self.init()
        store = Store(
            name="test_init",
            states=(
                ("state_1",0),("state_2",None)),
            reactives=(
                ("rct_state_1",self.formula_1,("state_1")),
                ("rct_state_2",self.formula_2,(),self.rct_state)
                )
        )
        assert store.get("state_1") == 0
        assert store.get("state_2") == None
        assert tuple(store.get("rct_state_1")) == tuple(range(0))
        assert store.get("rct_state_2") == self.rct_state.get()
        self.store = store
