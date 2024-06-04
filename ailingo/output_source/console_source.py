from dataclasses import dataclass

from rich import print
from rich.markdown import Markdown


@dataclass
class ConsoleOutputSource:
    path: str = "(console)"
    readable: bool = False
    markdown: bool = False

    def read(self) -> str:
        raise NotImplementedError("ConsoleOutputSource is not readable")

    def write(self, text: str):
        if self.markdown:
            print(Markdown(text))
        else:
            print(text)

    def exists(self) -> bool:
        return False
