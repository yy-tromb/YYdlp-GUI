from typing import TypeVar, Generic, Callable, Literal, TypeAlias, Any, Final
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass

T = TypeVar("T")


class IState(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> T | None:
        raise NotImplementedError()

    @abstractmethod
    def bind(self, *observers: Callable[[T | None], None]):
        raise NotImplementedError()


class State(IState, Generic[T]):
    """
When value is changed( setted by state_instance.set() ), functions( setted by state_instance.bind() ) is executed.

This is based in [this article: Python(Flet)でリアクティブなUIを作る方法を考える]\
(https://qiita.com/ForestMountain1234/items/64edacd5275c1ce4c943).
And I did a little changes.
Thanks to ForestMountain1234
[ForestMountain1234's GitHub](https://github.com/ForestMountain1234)
[ForestMountain1234's Qiita](https://qiita.com/ForestMountain1234/)"""  # noqa: E501

    def __init__(self, value: T | None = None) -> None:
        self.__value = value
        self.__observers: set[Callable[[T | None], None]] = set()

    def get(self) -> T | None:
        return self.__value

    def set(self, new_value: T):
        if self.__value != new_value:
            self.__value = new_value
            for observer in self.__observers:
                observer(self.__value)

    def bind(self, observers: tuple[Callable[[T | None], None]]):
        for observer in observers:
            if observer in self.__observers:
                raise ValueError()
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

    def __init__(self, formula: Callable[[IState,...], T],
                reliance_states: tuple[IState] | tuple[()] = (),
                reliance_state_keywords: dict[str,IState] = {}
                ):
        if reliance_states is None and reliance_state_keywords is None:
            raise ValueError()

        self.__reliances: tuple[IState] | tuple[()] = reliance_states
        self.__reliance_keywords: dict[str,IState] = reliance_state_keywords
        self.__value: T = formula(*self.__reliances,**self.__reliance_keywords)
        self.__formula = formula
        self.__observers: set[Callable[[T], None]] = set()

        # --original comment--
        # 依存関係にあるStateが変更されたら、再計算処理を実行するようにする
        for state in reliance_states:
            state.bind((lambda _: self.update()))
        for state in reliance_state_keywords.values():
            state.bind((lambda _: self.update()))

    def get(self) -> T | None:
        return self.__value

    def update(self):
        # --original comment--
        # コンストラクタで渡された計算用の関数を再度呼び出し、値を更新する
        new_value = self.__formula(*self.__reliances,**self.__reliance_keywords)
        if self.__value != new_value:
            self.__value = new_value
            for observer in self.__observers:
                observer(new_value)
                # --original comment--
                # 変更時に各observerに通知する

    def bind(self, *observers: Callable[[T], None]):
        for observer in observers:
            if observer in self.__observers:
                raise ValueError()
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
ReactiveStateDataType: TypeAlias = tuple[str, Callable[[IState,...], Any], tuple[IState, ...], dict[str,IState]]

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
        This method is equal `Store.state(("key",None),("key2",))`
        """
        for key in keys:
            if key in self.__states:
                raise KeyError()
            else:
                self.__states[key] = State(None)

    def reactive(self, *data_sets: ReactiveStateDataType) -> None:
        for set_ in data_sets:
            if set_[0] in self.__states:
                raise KeyError()
            else:
                self.__states[set_[0]] = ReactiveState(set_[1], set_[2],set_[3])

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
            
    def drop_store(self,*names: str) -> None:
        for name in names:
            self.__stores[name].drop_self()
            del self.__stores[name]
            
    def drop_self(self) -> None:
        for ondrop in self.__ondrops:
            ondrop()
            del self

    def ondrop(self, names: tuple[str], *ondrops: Callable) -> None:
        for name in names:
            self.__stores[name].ondrop_self(*ondrops)

    def ondrop_self(self, *ondrops: Callable) -> None:
        for ondrop in ondrops:
            if ondrop in self.__ondrops:
                raise ValueError()
            else:
                self.__ondrops.add(ondrop)

    def bind(self, states: tuple[str], *observers: Callable) -> None:
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
