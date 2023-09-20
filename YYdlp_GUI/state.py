from typing import TypeVar, Generic, Callable, Union
import abc

T = TypeVar("T")


class IState(Generic[T], metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self) -> T | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def _update(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def bind(self, observer: Callable):
        raise NotImplementedError()


class State(IState,Generic[T]):
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
            self._update()

    def _update(self):
        for observer in self.__observers:
            observer(self.__value)

    def bind(self, observer: Callable):
        self.__observers.append(observer)


class ReactiveState(IState,Generic[T]):

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

    def __init__(
        self, formula: Callable[[], T], reliance_states: list[IState]
    ):
        # reliance_group is being designed and prepared

        self.__value = State(formula())
        # --original comment--
        # 通常のStateクラスとは違い、valueがStateである

        self.__formula = formula
        self.__observers: list[Callable[[T | None], None]] = []

        for state in reliance_states:
            # --original comment--
            # 依存関係にあるStateが変更されたら、再計算処理を実行するようにする
            state.bind(lambda: self._update())

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

    def bind(self, observer):
        self.__observers.append(observer)
        # --original comment--
        # 変更時に呼び出す為のリストに登録


TState = IState | State | ReactiveState  # StateGroup
