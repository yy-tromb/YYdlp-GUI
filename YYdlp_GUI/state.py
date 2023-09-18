from typing import TypeVar, Generic, Union, Callable

T = TypeVar('T')


class State(Generic[T]): 
"""
When value is changed( setted by .set() ), functions( setted by .bind() ) is executed.  
This is based in [this article: Python(Flet)でリアクティブなUIを作る方法を考える](https://qiita.com/ForestMountain1234/items/64edacd5275c1ce4c943). And I did a little changes.  
Thanks to ForestMountain1234  
[ForestMountain1234's GitHub](https://github.com/ForestMountain1234)  
[ForestMountain1234's Qiita](https://qiita.com/ForestMountain1234/)
"""

     def __init__(self, value: T,group: str | None=None): 
         self.__value = value 
         self.__observers: list[Callable[T]] = [] 
         self.group = group
  
     def get(self): 
         return self.__value 
  
     def set(self, new_value: T): 
         if self.__value != new_value: 
             self.__value = new_value 
             self.update()

    def update():
      for observer in self.__observers: 
                 observer(self.__value) 
  
     def bind(self, observer): 
         self.__observers.append(observer)
