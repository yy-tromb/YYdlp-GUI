from typing import TypeVar
import pytest
from YYdlp_GUI.state import State

T = TypeVar("T")


@pytest.mark.parametrize(("value"), [None, 0, "", (), [], {}])
def test_state_get(value: T) -> None:
    state = State(value)
    assert state.get() == value
