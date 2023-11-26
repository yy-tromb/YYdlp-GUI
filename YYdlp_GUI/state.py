from typing import TypeVar, Generic, Callable, Literal, TypeAlias, Any, Final
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass

T = TypeVar("T")


class IState(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def get(self) -> T | None:
        raise NotImplementedError()

    @abstractmethod
    def bind(self, observers: list[Callable[[T | None], None]]):
        raise NotImplementedError()


class State(IState, Generic[T]):
    """
    When value is changed( setted by .set() ), functions( setted by .bind() ) is executed.

    This is based in [this article: Python(Flet)でリアクティブなUIを作る方法を考える](https://qiita.com/ForestMountain1234/items/64edacd5275c1ce4c943). And I did a little changes.
    Thanks to ForestMountain1234
    [ForestMountain1234's GitHub](https://github.com/ForestMountain1234)
    [ForestMountain1234's Qiita](https://qiita.com/ForestMountain1234/)"""  # noqa: E501

    def __init__(self, value: T | None = None) -> None:
        self.__value = value
        self.__observers: list[Callable[[T | None], None]] = []

    def get(self) -> T | None:
        return self.__value

    def set(self, new_value: T):
        if self.__value != new_value:
            self.__value = new_value
            for observer in self.__observers:
                observer(self.__value)

    def bind(self, observers: list[Callable[[T | None], None]]):
        self.__observers.extend(observers)


class ReactiveState(IState, Generic[T]):

    """
    When reliance states( State or ReactiveState ) or reliance state group is updated, functions( setted by .bind() ) is executed.

    This is based in [this article: Python(Flet)でリアクティブなUIを作る方法を考える](https://qiita.com/ForestMountain1234/items/64edacd5275c1ce4c943). And I did a little changes.
    Thanks to ForestMountain1234
    [ForestMountain1234's GitHub](https://github.com/ForestMountain1234)
    [ForestMountain1234's Qiita](https://qiita.com/ForestMountain1234/)"""  # noqa: E501

    # --original comment--
    # formula: State等を用いて最終的にT型の値を返す関数。
    # 例えばlambda value: f'value:{value}'といった関数を渡す。
    # reliance_states: 依存関係にあるState, ReactiveStateをlist形式で羅列する。

    def __init__(self, formula: Callable[[], T], reliance_states: tuple[IState,...]):
        # reliance_group is being designed and prepared

        self.__value = State(formula())
        # --original comment--
        # 通常のStateクラスとは違い、valueがStateである

        self.__formula = formula
        self.__observers: list[Callable[[T | None], None]] = []

        for state in reliance_states:
            # --original comment--
            # 依存関係にあるStateが変更されたら、再計算処理を実行するようにする
            state.bind([lambda _: self._update()])

    def get(self) -> T | None:
        return self.__value.get()

    def _update(self):
        old_value = self.__value.get()
        # --original comment--
        # コンストラクタで渡された計算用の関数を再度呼び出し、値を更新する
        self.__value.set(self.__formula())

        if old_value != self.__value.get():
            for observer in self.__observers:
                observer(self.__value.get())
                # --original comment--
                # 変更時に各observerに通知する

    def bind(self, observers: list[Callable[[T | None], None]]):
        self.__observers.extend(observers)
        # --original comment--
        # 変更時に呼び出す為のリストに登録


@dataclass
class StoreKey:
    key: str
    kind: Literal["State", "ReactiveState"]
    state: State | ReactiveState


class IStore:
    pass


class IStateRef(IState, Generic[T]):
    pass


class IReactiveStateRef(IState, Generic[T]):
    pass

TStateDataPair: TypeAlias= tuple[str, Any | None]
TReactiveStateDataSet: TypeAlias=tuple[str, Callable[[],Any] ,tuple[IState, ...]]

class Store(IStore):
    def __init__(
        self,
        name: str,
        states: tuple[TStateDataPair, ...] | None = None,
        state_keys: tuple[str] | None = None,
        reactives: tuple[TReactiveStateDataSet,...] | None = None,
    ) -> None:
        # initialise object
        self.__states: dict[str, State | ReactiveState] = {}
        self.__stores: dict[str,IStore] = {}
        self.__ondrops: set[Callable[[],None]] = set()
        self.__observers: set[Callable[[],None]] = set()
        # process arguments
        self.name: str = name
        if states is not None:
            self.state(*states)
        if state_keys is not None:
            self.add_state(*state_keys)
        if reactives is not None:
            self.reactive(*reactives)

    def state(self, *pairs: TStateDataPair) -> None:
        for pair in pairs:
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

    def reactive(self, *sets: TReactiveStateDataSet) -> None:
        for set_ in sets:
            if set_[0] in self.__states:
                raise KeyError()
            else:
                self.__states[set_[0]] = ReactiveState(set_[1],set_[2])

    def store(
        self,
        name: str,
        states: tuple[TStateDataPair, ...] | None = None,
        state_keys: tuple[str] | None = None,
        reactives: tuple[TReactiveStateDataSet,...] | None = None,
    ) -> IStore:
        if name in self.__stores:
            raise KeyError()
        else:
            store = Store(name, states, state_keys, reactives)
            self.__stores[name] = store
            return store

    def remove(self,*keys: str) -> None:
        for key in keys:
            del self.__states[key]

    def drop_store(self) -> None:
        pass
    
    def ondrop(self) -> None:
        pass
    
    def ondrop_self(self) -> None:
        pass

    def bind(self,states: tuple[str],*observers : Callable) -> None:
        pass
    
    def bind_store(self,stores: tuple[str],*observers : Callable) -> None:
        pass
    
    def bind_self(self,*observers : Callable) -> None:
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


TState: TypeAlias = IState | State | ReactiveState
