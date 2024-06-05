from typing import Protocol


class OutputSource(Protocol):
    def write(self, text: str): ...

    def read(self) -> str: ...

    def exists(self) -> bool: ...

    @property
    def path(self) -> str: ...

    @property
    def readable(self) -> bool: ...
