from typing import Protocol


class InputSource(Protocol):
    def read(self) -> str: ...

    @property
    def path(self) -> str: ...
