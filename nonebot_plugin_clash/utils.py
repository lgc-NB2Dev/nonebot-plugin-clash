import base64
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


def auto_convert_unit(value: float, round_n: int = 2, suffix: str = "") -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]

    unit = None
    for x in units:
        if value < 1000:
            unit = x
            break
        value /= 1024

    return f"{value:.{round_n}f} {unit or units[-1]}{suffix}"


async def b2url(data: bytes, mime: str = "image/png") -> str:
    b64 = base64.b64encode(data).decode()
    return f"data:{mime};base64,{b64}"
