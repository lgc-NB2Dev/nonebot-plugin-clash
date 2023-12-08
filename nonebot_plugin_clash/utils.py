from typing import Generic, Iterable, List, Optional, TypeVar, Union, overload
from typing_extensions import Self

T = TypeVar("T")
T2 = TypeVar("T2")


class SizedList(Generic[T], List[T]):
    def __init__(
        self,
        iterable: Optional[Iterable[T]] = None,
        size: Optional[int] = None,
    ) -> None:
        if iterable is None:
            super().__init__()
        else:
            super().__init__(iterable)
        self.size = size
        self._handle_overflow()

    @property
    def last(self) -> Optional[T]:
        if self:
            return self[-1]
        return None

    def _handle_overflow(self) -> None:
        if self.size is None:
            return
        while len(self) > self.size:
            self.pop(0)

    def append(self, item: T) -> None:
        super().append(item)
        self._handle_overflow()

    def extend(self, items: Iterable[T]) -> None:
        super().extend(items)
        self._handle_overflow()

    def insert(self, index: int, item: T) -> None:
        super().insert(index, item)
        self._handle_overflow()

    @overload
    def __add__(self, items: Iterable[T]) -> "SizedList[T]":
        ...

    @overload
    def __add__(self, items: Iterable[T2]) -> "SizedList[Union[T, T2]]":
        ...

    def __add__(self, items):
        return SizedList((*self, *items), size=self.size)

    def __iadd__(self, items: Iterable[T]) -> Self:
        self.extend(items)
        return self


def camel_case(string: str, upper_first: bool = False) -> str:
    pfx, *rest = string.split("_")
    if upper_first:
        pfx = pfx.capitalize()
    sfx = "".join(x.capitalize() for x in rest)
    return f"{pfx}{sfx}"
