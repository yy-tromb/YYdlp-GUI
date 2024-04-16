from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Final, Generic, Literal, TypeAlias, TypeVar, Unpack

_T = TypeVar("_T")


class RedundancyError(Exception):
    def __init__(self, target: Any | None, message: str = "") -> None:
        self.message = message
        self.target = target

    def __str__(self) -> str:
        return f"""
{self.target} is Redundancy.
日本語:{self.target}は重複しています。
additional message:
{self.message}"""


class EssentialError(Exception):
    def __init__(self, target: Any | None, message: str = "") -> None:
        self.message = message
        self.target = target

    def __str__(self) -> str:
        return f"""
Essentials was not given. given {self.target}
日本語:必要なものが与えられませんでした。{self.target}が与えられました。
additional message:
{self.message}"""


class IState(Generic[_T], metaclass=ABCMeta):
    """State Interface

    Methods:
        get() -> _T | None
        bind(*observers: Callable[[_T | None], None]) -> None

    Raises:
        NotImplementedError: if implements class do not implement this method,
                                NotImplementedError is raised
    """

    # __value: T
    # __observers: set[Callable[[T], None]]

    @abstractmethod
    def get(self) -> _T | None:
        """return current value"""
        raise NotImplementedError()

    @abstractmethod
    def bind(self, *observers: Callable[[_T | None], None]) -> None:
        """bind observer functions

        Raises:
            RedundancyError: if observer given by arguments have already binded,
                                RedudancyError is raised.
        """
        raise NotImplementedError()

    @abstractmethod
    def unbind(self, *observers: Callable[[_T | None], None]) -> None:
        raise NotImplementedError()


class State(IState, Generic[_T]):
    """management value by state.  \


When value is changed( setted by state_instance.set() ),\
functions( setted by state_instance.bind() ) is executed.

This is based in [this article: Python(Flet)でリアクティブなUIを作る方法を考える]\
(https://qiita.com/ForestMountain1234/items/64edacd5275c1ce4c943).
And I did a little changes.
Thanks to ForestMountain1234
[ForestMountain1234's GitHub](https://github.com/ForestMountain1234)
[ForestMountain1234's Qiita](https://qiita.com/ForestMountain1234/)"""

    def __init__(self, value: _T | None = None) -> None:
        self.__value: _T | None = value
        self.__observers: set[Callable[[_T | None], None]] = set()

    def get(self) -> _T | None:
        """return current value"""
        return self.__value

    def set(self, new_value: _T) -> None:
        """set new value

        binded observer functions is executed.

        Note:
            if new value is the same as old value,
            new value isn't assigned.
        """
        if self.__value != new_value:
            self.__value = new_value
            self_observers = self.__observers  # faster
            for observer in self_observers:
                observer(self.__value)

    def bind(self, *observers: Callable[[_T | None], None]) -> None:
        """bind observer functions

        Raises:
            RedundancyError: if observer given by arguments have already binded,
                                RedudancyError is raised.
        """
        prev_len = len(self.__observers)
        self.__observers.update(observers)
        if len(self.__observers) < prev_len + len(observers):
            raise RedundancyError(
                target=tuple(
                    observer for observer in observers if observer in self.__observers
                ),
                message="redudancy observer was given.",
            )
        # --original comment--
        # 変更時に呼び出す為の集合に登録

    def unbind(self, *observers: Callable[[_T | None], None]) -> None:
        """unbind observer functions."""
        if not observers:
            self.__observers.clear()
        else:
            self_observers = self.__observers  # faster
            for observer in observers:
                self_observers.remove(observer)


class ReactiveState(IState, Generic[_T]):
    """
    When reliance states( State or ReactiveState ) is updated,
    functions( setted by reactivestate_instance.bind() ) is executed.

    This is based in [this article: Python(Flet)でリアクティブなUIを作る方法を考える]
    (https://qiita.com/ForestMountain1234/items/64edacd5275c1ce4c943). And I did a little changes.
    Thanks to ForestMountain1234
    [ForestMountain1234's GitHub](https://github.com/ForestMountain1234)
    [ForestMountain1234's Qiita](https://qiita.com/ForestMountain1234/)"""  # noqa: E501

    # --original comment--
    # formula: State等を用いて最終的にT型の値を返す関数。
    # 例えばlambda value: f'value:{value}'といった関数を渡す。
    # reliance_states: 依存関係にあるState, ReactiveStateをtupleで羅列する。

    def __init__(
        self,
        formula: Callable[[*tuple[Any,...]], _T],
        # This is Python3.11 feature.
        # Can't use in PyPy latest 3.10
        reliance_states: tuple[IState, ...],
    ) -> None:
        self.__reliances: tuple[IState] = reliance_states
        self.__value: _T = formula(*(reliance.get() for reliance in self.__reliances))
        self.__formula = formula
        self.__observers: set[Callable[[_T], None]] = set()

        # --original comment--
        # 依存関係にあるStateが変更されたら、再計算処理を実行するようにする
        for state in reliance_states:
            state.bind(self.__update)

    def get(self) -> _T | None:
        """return current value"""
        return self.__value

    def __update(self) -> None:
        # --original comment--
        # コンストラクタで渡された計算用の関数を再度呼び出し、値を更新する
        new_value = self.__formula(*(reliance.get() for reliance in self.__reliances ))
        if self.__value != new_value:
            self.__value = new_value
            self_observers = self.__observers  # faster
            for observer in self_observers:
                observer(new_value)
                # --original comment--
                # 変更時に各observerに通知する

    def bind(self, *observers: Callable[[_T], None]) -> None:
        """bind observer functions

        Raises:
            RedundancyError: if observer given by arguments have already binded,
                                RedudancyError is raised.
        """
        prev_len = len(self.__observers)
        self.__observers.update(observers)
        if len(self.__observers) < prev_len + len(observers):
            raise RedundancyError(
                target=tuple(
                    observer for observer in observers if observer in self.__observers
                ),
                message="redudancy observer was given.",
            )
        # --original comment--
        # 変更時に呼び出す為の集合に登録

    def unbind(self, *observers: Callable[[_T | None], None]):
        if not observers:
            self.__observers.clear()
        else:
            self_observers = self.__observers  # faster
            for observer in observers:
                self_observers.remove(observer)


@dataclass
class StoreKey:
    key: str
    kind: Literal["State", "ReactiveState"]
    state: State | ReactiveState


class IStore(metaclass=ABCMeta):
    pass
    ########################
    # ToDo!!!!!!!!!!!!!!!!!#
    ########################


class IStateRefs(Generic[_T],metaclass=ABCMeta):
    pass

StateDataType: TypeAlias = tuple[str, Any | None]
ReactiveStateDataType: TypeAlias = tuple[
    str,
    Callable[[*tuple[IState, ...]], Any],
    # *tuple[] is Python3.11 feature.
    # Can't use in PyPy latest 3.10
    tuple[str, ...],
    tuple[IState, ...],
]


class Store(IStore):
    def __init__(
        self,
        name: str,
        states: tuple[StateDataType, ...] | None = None,
        state_keys: tuple[str] | None = None,
        reactives: tuple[ReactiveStateDataType, ...] | None = None,
    ) -> None:
        # initialise object
        self.__is_enabled_bind_self: bool = False
        self.__states: dict[str, State | ReactiveState] = {}
        self.__stores: dict[str, IStore] = {}
        self.__on_drops: set[Callable[[], None]] = set()
        self.__observers: set[Callable[[], None]] = set()
        # process arguments
        self.name: str = name
        if states is not None:
            self.state(*states)
        if state_keys is not None:
            self.state_keys(*state_keys)
        if reactives is not None:
            self.reactive(*reactives)

    def __call_observer(self) -> None:
        for observer in self.__observers:
            observer(self)

    def __enable_bind_self(self):
        self.__is_enabled_bind_self = True
        for state in self.__states:
            state.bind(lambda _: self.__call_observer())
        for store in self.__stores:
            store.bind(lambda _: self.__call_observer())

    def state(self, *state_data: StateDataType) -> None:
        self_states = self.__states  # faster
        for data in state_data:
            if data[0] in self_states:
                raise RedundancyError(
                    target=data[0], message=f"""key:"{data[0]}" has already existed."""
                )
            else:
                self_states[data[0]] = State(data[1])
                if self.__is_enabled_bind_self:
                    self_states[data[0]].bind(self.__call_observer)

    def state_keys(self, *keys: str) -> None:
        """add_state
        This method is equal `store_instance.state(("key",None),("key2",))`
        """
        self_states = self.__states  # faster
        for key in keys:
            if key in self_states:
                raise RedundancyError(
                    target=key, message=f"""key:"{key}" has already existed."""
                )
            else:
                self_states[key] = State(None)
                if self.__is_enabled_bind_self:
                    self_states[key].binf(self.__call_observer)

    def reactive(self, *reactive_state_data: ReactiveStateDataType) -> None:
        self_states = self.__states  # faster
        for data in reactive_state_data:
            if data[0] in self_states:
                raise RedundancyError(
                    target=data[0], message=f"""key:"{data[0]}" has already existed."""
                )
            else:
                reliances_in_store = (self.__states[key] for key in data[2])
                self_states[data[0]] = ReactiveState(data[1], (*reliances_in_store,*data[2]))
                if self.__is_enabled_bind_self:
                    self_states[data[0]].bind(self.__call_observer)

    def store(
        self,
        name: str,
        states: tuple[StateDataType, ...] | None = None,
        state_keys: tuple[str] | None = None,
        reactives: tuple[ReactiveStateDataType, ...] | None = None,
    ) -> IStore:
        store = Store(name, states, state_keys, reactives)
        if name in self.__stores:
            raise RedundancyError(
                target=name, message=f"""Store of name:"{name}" has already existed."""
            )
        else:
            self.__stores[name] = store
            if self.__is_enabled_bind_self:
                self.__stores[name].bind(self.__call_observer)
        return store

    def remove(self, *keys: str) -> None:
        for key in keys:
            del self.__states[key]

    def drop_store(self, *names: str) -> None:
        for name in names:
            del self.__stores[name]

    def on_drop(
        self, names: tuple[str], on_drops: tuple[Callable[[], None], ...]
    ) -> None:
        for name in names:
            self.__stores[name].on_drop_self(*on_drops)

    def on_drop_self(self, *on_drops: tuple[Callable[[], None]]) -> None:
        prev_len = len(self.__on_drops)
        self.__on_drops.update(on_drops)
        if len(self.__on_drops) < prev_len + len(on_drops):
            raise RedundancyError(
                target=tuple(
                    on_drop for on_drop in on_drops if on_drop in self.__on_drops
                )
            )

    def __del__(self):
        for on_drop in self.__on_drops:
            on_drop()

    def bind_states(
        self, keys: tuple[str], observers: tuple[Callable[[Any | None], None]]
    ) -> None:
        self_states = self.__states  # faster
        for key in keys:
            if key in self_states:
                self_states[key].bind(*observers)
            else:
                raise KeyError(f"""State or ReactiveState of "{key}" is not found.""")

    def bind_store(
        self, keys: tuple[str], observers: tuple[Callable[[IStore], None]]
    ) -> None:
        self_stores = self.__stores  # faster
        for key in keys:
            if key in self_stores:
                self_stores[key].bind(*observers)

    def bind(self, *observers: Callable[[IStore], None]) -> None:
        if self.__is_enabled_bind_self is False:
            self.__enable_bind_self()
        prev_len = len(self.__observers)
        self.__observers.update(observers)
        if len(self.__observers) < prev_len + len(observers):
            raise RedundancyError(
                target=tuple(
                    observer for observer in observers if observer in self.__observers
                ),
                message="redudancy observer was given.",
            )

    def unbind(
        self,
        keys: tuple[str],
        observers: tuple[Callable[[Any | None | IStore], None]] | None = None,
    ) -> None:
        self_states = self.__states  # faster
        for key in keys:
            if key in self_states:
                self_states[key].unbind(*observers)
            else:
                raise KeyError(f"""State or ReactiveState of "{key}" is not found.""")

    def unbind_store(
        self,
        keys: tuple[str],
        observers: tuple[Callable[[Any | None | IStore], None]] | None = None,
    ) -> None:
        self_stores = self.__stores  # faster
        for key in keys:
            if key in self_stores:
                self_stores[key].unbind_self(*observers)
            else:
                raise KeyError(f"""State or ReactiveState of "{key}" is not found.""")

    def unbind_self(self, *observers: Callable[[IStore], None]) -> None:
        if not observers:
            self.__observers.clear()
        else:
            self_observers = self.__observers  # faster
            for observer in observers:
                self_observers.remove(observer)

    def set(self, keys: tuple[str], value: Any) -> None:
        self_states = self.__states  # faster
        for key in keys:
            if key in self_states and isinstance(self_states[key], State):
                self_states[key].set(value)
            elif key not in self_states:
                raise KeyError(key)
            elif not isinstance(self_states[key], State):
                raise TypeError(self_states[key])

    def get(self, key: str) -> Any:
        return self.__states[key].get()

    def gets(self, keys: tuple[str]) -> tuple[Any]:
        return (self.__states[key].get() for key in keys)

    def gets_dict(self, keys: tuple[str]) -> dict[str, Any]:
        return {key: self.__states[key].get() for key in keys}

    def get_store(self, name: str) -> IStore:
        return self.__stores[name]

    def refs(self, *keys: str) -> IStateRefs:
        return StateRefs(store=self, keys=keys)

class StateRefs(IStateRefs):
    def __init__(
        self,
        store: IStore,
        keys: tuple[str],
    ) -> None:
        self.__store: IStore = store
        self.__keys: tuple[str] = keys
        self.__observers: set[Callable] = set()
        for key in keys:
            store[key].bind(self.__call_observer)

    def keys(self) -> tuple[str]:
        return self.__keys

    def gets_dict(self) -> dict[str, Any]:
        return self.__store.gets_dict(self.__keys)

    def bind_states(
        self, keys: tuple[str], observers: tuple[Callable[[Any | None], None]]
    ) -> None:
        for key in keys:
            if key not in self.__keys:
                raise KeyError(key)
        self.__store.bind(keys, observers)

    def bind(self, *observers: Callable):
        prev_len = len(self.__observers)
        self.__observers.update(observers)
        if len(self.__observers) < prev_len + len(observers):
            raise RedundancyError(
                target=tuple(
                    observer for observer in observers if observer in self.__observers
                ),
                message="redudancy observer was given.",
            )

    def __call_observer(self) -> None:
        self_observers = self.__observers
        for observer in self_observers:
            observer(self)

StateType: TypeAlias = IState | State | ReactiveState
