from dataclasses import dataclass
from typing import Iterable

from rich import print
from rich.live import Live
from rich.markdown import Markdown


@dataclass
class ConsoleOutputSource:
    path: str = "(console)"
    readable: bool = False
    markdown: bool = False

    def read(self) -> str:
        raise NotImplementedError("ConsoleOutputSource is not readable")

    def write_stream(self, text: Iterable[str]):
        with Live(vertical_overflow="visible") as live:
            received_text = ""
            for chunk in text:
                received_text += chunk
                if self.markdown:
                    live.update(Markdown(received_text))
                else:
                    live.update(received_text)

    def write(self, text: str):
        if self.markdown:
            print(Markdown(text))
        else:
            print(text)

    def exists(self) -> bool:
        return False
