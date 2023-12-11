from typing import (
    TypeVar,
    Generic,
    Callable,
    Literal,
    TypeAlias,
    Any,
    Final,
)
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass

T = TypeVar("T")


class RedundancyError(Exception):
    def __init__(self, target: Any | None, message: str = "") -> None:
        self._message = message
        self._target = target

    def __str__(self) -> str:
        return super().__str__(
            f"""{self._target} is Redundancy.
日本語:{self._target}は重複しています。
additional message:
{self._message}"""
        )


class EssentialError(Exception):
    def __init__(self, target: Any | None, message: str = "") -> None:
        self._message = message
        self._target = target

    def __str__(self) -> str:
        return super().__str__(
            f"""Essentials was not given. given {self._target}
日本語:必要なものが与えられませんでした。{self._target}が与えられました。
additional message:
{self._message}"""
        )


class IState(Generic[T], metaclass=ABCMeta):
    # __value: T
    # __observers: set[Callable[[T], None]]

    @abstractmethod
    def get(self) -> T | None:
        raise NotImplementedError()

    @abstractmethod
    def bind(self, *observers: Callable[[T | None], None]):
        raise NotImplementedError()


class State(IState, Generic[T]):
    """
When value is changed( setted by state_instance.set() ),\
functions( setted by state_instance.bind() ) is executed.

This is based in [this article: Python(Flet)でリアクティブなUIを作る方法を考える]\
(https://qiita.com/ForestMountain1234/items/64edacd5275c1ce4c943).
And I did a little changes.
Thanks to ForestMountain1234
[ForestMountain1234's GitHub](https://github.com/ForestMountain1234)
[ForestMountain1234's Qiita](https://qiita.com/ForestMountain1234/)"""

    def __init__(self, value: T | None = None) -> None:
        self.__value: T | None = value
        self.__observers: set[Callable[[T | None], None]] = set()

    def get(self) -> T | None:
        return self.__value

    def set(self, new_value: T):
        if self.__value != new_value:
            self.__value = new_value
            for observer in self.__observers:
                observer(self.__value)

    def bind(self, *observers: Callable[[T | None], None]):
        for observer in observers:
            if observer in self.__observers:
                raise RedundancyError(
                    target=observer, message="redudancy observer was given"
                )
            else:
                self.__observers.add(observer)


class ReactiveState(IState, Generic[T]):

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
        formula: Callable[[*tuple[IState, ...]], T],
        # This is Python3.11 feature.
        # Can't use in PyPy latest 3.10
        reliance_states: tuple[IState] | None = None,
    ):
        if reliance_states is None:
            raise EssentialError(
                target=reliance_states, message="reliance_states is essential."
            )

        self.__reliances: tuple[IState] = reliance_states
        self.__value: T = formula(*self.__reliances)
        self.__formula = formula
        self.__observers: set[Callable[[T], None]] = set()

        # --original comment--
        # 依存関係にあるStateが変更されたら、再計算処理を実行するようにする
        for state in reliance_states:
            state.bind(lambda _: self.update())

    def get(self) -> T | None:
        return self.__value

    def update(self):
        # --original comment--
        # コンストラクタで渡された計算用の関数を再度呼び出し、値を更新する
        new_value = self.__formula(*self.__reliances)
        if self.__value != new_value:
            self.__value = new_value
            for observer in self.__observers:
                observer(new_value)
                # --original comment--
                # 変更時に各observerに通知する

    def bind(self, *observers: Callable[[T], None]):
        for observer in observers:
            if observer in self.__observers:
                raise RedundancyError(
                    target=observer, message="redudancy observer was given"
                )
            else:
                self.__observers.add(observer)
        # --original comment--
        # 変更時に呼び出す為のリストに登録


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


class IStateRef(IState, Generic[T]):
    pass


class IReactiveStateRef(IState, Generic[T]):
    pass


StateDataType: TypeAlias = tuple[str, Any | None]
ReactiveStateDataType: TypeAlias = tuple[
    str,
    Callable[[*tuple[IState, ...]], Any],
    # This is Python3.11 feature.
    # Can't use in PyPy latest 3.10
    tuple[IState, ...] | None,
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
        self.__ondrops: set[Callable[[], None]] = set()
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
                raise KeyError()
            else:
                self.__states[pair[0]] = State(pair[1])

    def add_state(self, *keys: str) -> None:
        """add_state
        This method is equal `store_instance.state(("key",None),("key2",))`
        """
        for key in keys:
            if key in self.__states:
                raise KeyError()
            else:
                self.__states[key] = State(None)

    def reactive(self, *data_sets: ReactiveStateDataType) -> None:
        for data in data_sets:
            if data[0] in self.__states:
                raise KeyError()
            else:
                self.__states[data[0]] = ReactiveState(data[1], data[2])

    def store(
        self,
        name: str,
        states: tuple[StateDataType, ...] | None = None,
        state_keys: tuple[str] | None = None,
        reactives: tuple[ReactiveStateDataType, ...] | None = None,
    ) -> IStore:
        if name in self.__stores:
            raise KeyError()
        else:
            store = Store(name, states, state_keys, reactives)
            self.__stores[name] = store
            return store

    def remove(self, *keys: str) -> None:
        for key in keys:
            del self.__states[key]

    def drop_store(self, *names: str) -> None:
        for name in names:
            del self.__stores[name]

    def ondrop(
        self, names: tuple[str], ondrops: tuple[Callable[[], None], ...]
    ) -> None:
        for name in names:
            self.__stores[name].ondrop_self(*ondrops)

    def ondrop_self(self, *ondrops: Callable[[], None]) -> None:
        for ondrop in ondrops:
            if ondrop in self.__ondrops:
                raise ValueError()
            else:
                self.__ondrops.add(ondrop)

    def __del__(self):
        for ondrop in self.__ondrops:
            ondrop()

    def bind(
        self, states: tuple[str], observers: tuple[Callable[[Any | None], None]]
    ) -> None:
        pass

    def bind_store(self, stores: tuple[str], *observers: Callable) -> None:
        pass

    def bind_self(self, *observers: Callable) -> None:
        pass

    def unbind(self) -> None:
        pass

    def set(self) -> None:
        pass

    def get_store(self, name: str) -> IStore:
        return self.__stores[name]

    def ref(self, key: str) -> IStateRef | IReactiveStateRef:  # type: ignore
        pass

    def refs(self, *key: str) -> tuple[IStateRef | IReactiveStateRef]:  # type: ignore
        pass

    def ref_s(self) -> IStateRef:  # type: ignore
        pass

    def refs_s(self) -> tuple[IStateRef]:  # type: ignore
        pass

    def ref_r(self) -> IReactiveStateRef:  # type: ignore
        pass

    def refs_r(self) -> tuple[IReactiveStateRef]:  # type: ignore
        pass


class StateRef(IStateRef, Generic[T]):
    def __init__(
        self,
        store: IStore,
        key: str,
    ) -> None:
        self.__store: IStore = store
        self.__key: str = key

    def get(self) -> None:
        pass

    def bind(self, observers: list[Callable[[T | None], None]]) -> None:
        pass

    def _update(self) -> None:
        pass


class ReactiveStateRef(IReactiveStateRef, Generic[T]):
    def __init__(
        self,
        store: IStore,
        key: str,
    ) -> None:
        self.__store: IStore = store
        self.__key: str = key


StateType: TypeAlias = IState | State | ReactiveState
