from typing import (
    TypeVar,
    Generic,
    Callable,
    Literal,
    TypeAlias,
    Any,
    Final,
    Unpack
)
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass

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
    def unbind(self,*observers: Callable[[_T | None], None]) -> None:
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
            self_observers = self.__observers # faster
            for observer in self__observers:
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

        def unbind(self,*observers: Callable[[_T | None], None]):
            if observers is ():
                self.__observers.clear()
            else:
                self_observers = self.__observers # faster
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
        formula: Callable[[*tuple[IState, ...]], _T],
        # This is Python3.11 feature.
        # Can't use in PyPy latest 3.10
        reliance_states: tuple[IState,...],
    ) -> None:
        self.__reliances: tuple[IState] = reliance_states
        self.__value: _T = formula(reliances_states)
        self.__formula = formula
        self.__observers: set[Callable[[_T], None]] = set()

        # --original comment--
        # 依存関係にあるStateが変更されたら、再計算処理を実行するようにする
        for state in reliance_states:
            state.bind(lambda _: self.update())

    def get(self) -> _T | None:
        """return current value"""
        return self.__value

    def update(self) -> None:
        # --original comment--
        # コンストラクタで渡された計算用の関数を再度呼び出し、値を更新する
        new_value = self.__formula(*self.__reliances)
        if self.__value != new_value:
            self.__value = new_value
            self_observers = self.__observers # faster
            for observer in self__observers:
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

    def unbind(self,*observers: Callable[[_T | None], None]):
        if observers is ():
            self.__observers.clear()
        else:
            self_observers = self.__observers # faster
            for observer in observers:
                self_observers.remove(observer)

@dataclass
class StoreKey:
    key: str
    kind: Literal["State", "ReactiveState"]
    state: State | ReactiveState


class IStore:
    pass
    ########################
    # ToDo!!!!!!!!!!!!!!!!!#
    ########################


class IStateRef(IState, Generic[_T]):
    pass


class IReactiveStateRef(IState, Generic[_T]):
    pass


StateDataType: TypeAlias = tuple[str, Any | None]
ReactiveStateDataType: TypeAlias = tuple[
    str,
    Callable[[*tuple[IState, ...]], Any],
    # *tuple[] is Python3.11 feature.
    # Can't use in PyPy latest 3.10
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
        self.__states: dict[str, State | ReactiveState] = {}
        self.__stores: dict[str, IStore] = {}
        self.__on_drops: set[Callable[[], None]] = set()
        self.__observers: set[Callable[[], None]] = set()
        # process arguments
        self.name: str = name
        if states is not None:
            self.state(*states)
        if state_keys is not None:
            self.add_state(*state_keys)
        if reactives is not None:
            self.reactive(*reactives)

    def state(self, *data_pairs: StateDataType) -> None:
        for pair in data_pairs:
            if pair[0] in self.__states:
                raise RedudancyError(target=pair[0],message=f"""key:"{}" has already existed.""")
            else:
                self.__states[pair[0]] = State(pair[1])

    def add_state(self, *keys: str) -> None:
        """add_state
        This method is equal `store_instance.state(("key",None),("key2",))`
        """
        for key in keys:
            if key in self.__states:
                raise RedundancyError(target=key,message=f"""key:"{key}" has already existed.""")
            else:
                self.__states[key] = State(None)

    def reactive(self, *data_sets: ReactiveStateDataType) -> None:
        for data in data_sets:
            if data[0] in self.__states:
                raise RedundancyError(target=data[0],message=f"""key:"{data[0]}" has already existed.""")
            else:
                self.__states[data[0]] = ReactiveState(data[1], data[2])

    def store(
        self,
        name: str,
        states: tuple[StateDataType, ...] | None = None,
        state_keys: tuple[str] | None = None,
        reactives: tuple[ReactiveStateDataType, ...] | None = None,
    ) -> IStore:
        store = Store(name, states, state_keys, reactives)
        self.__stores[name] = store
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
            raise RedundancyError(target=tuple(
                on_drop for on_drop in on_drops if on_drop in self.__on_drops
                ))

    def __del__(self):
        for on_drop in self.__on_drops:
            on_drop()

    def bind(
        self, keys: tuple[str], observers: tuple[Callable[[Any | None], None]]
    ) -> None:
        for key in keys:
            if key in self.__states:
                self.__states[key].bind(*observers)
            else:
                raise KeyError(f"""State or ReactiveState of "{key}" is not found.""")

    def bind_store(self, keys: tuple[str], observers: tuple[Callable[[Store],None]]) -> None:
        for key in keys:
            if key in self.__stores:
                self.__stores[key].bind_self(*observers)

    def bind_self(self, *observers: Callable[[Store],None]) -> None:
        prev_len = len(self.__observers)
        self.__observers.update(observers)
        if len(self.__observers) < prev_len + len(observers):
            raise RedundancyError(
                target=tuple(
                    observer for observer in observers if observer in self.__observers
                ),
                message="redudancy observer was given.",
            )

    def unbind(self,keys: tuple[str],
               observers: tuple[Callable[[Any | None | Store],None]] | None = None) -> None:
        for key in keys:
            if key in self.__states:
                self.__states[key].unbind(*observers)
            else:
                raise KeyError(f"""State or ReactiveState of "{key}" is not found.""")
    
    def unbind_store(self,keys: tuple[str],
               observers: tuple[Callable[[Any | None | Store],None]] | None = None) -> None:
        for key in keys:
            if key in self.__stores:
                self.__stores[key].unbind_self(*observers)
            else:
                raise KeyError(f"""State or ReactiveState of "{key}" is not found.""")
    
    def unbind_self(self,*observers: Callable[[Store],None]) -> None:
        if observers is ():
            self.__observers.clear()
        else:
            self_observers = self.__observers # faster
            for observer in observers:
                self_observers.remove(observer)

    def set(self) -> None:
        pass

    def get_store(self, name: str) -> IStore:
        return self.__stores[name]

    def ref(self, key: str) -> IStateRef | IReactiveStateRef:  # type: ignore
        pass

    def refs(self, *key: str) -> tuple[IStateRef | IReactiveStateRef,...]:  # type: ignore
        pass

    def ref_s(self) -> IStateRef:  # type: ignore
        pass

    def refs_s(self) -> tuple[IStateRef,...]:  # type: ignore
        pass

    def ref_r(self) -> IReactiveStateRef:  # type: ignore
        pass

    def refs_r(self) -> tuple[IReactiveStateRef,...]:  # type: ignore
        pass


class StateRef(IStateRef, Generic[_T]):
    def __init__(
        self,
        store: IStore,
        key: str,
    ) -> None:
        self.__store: IStore = store
        self.__key: str = key

    def get(self) -> None:
        pass

    def bind(self, observers: list[Callable[[_T | None], None]]) -> None:
        pass

    def _update(self) -> None:
        pass


class ReactiveStateRef(IReactiveStateRef, Generic[_T]):
    def __init__(
        self,
        store: IStore,
        key: str,
    ) -> None:
        self.__store: IStore = store
        self.__key: str = key


StateType: TypeAlias = IState | State | ReactiveState
