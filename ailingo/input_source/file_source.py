from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileInputSource:
    path: str

    def __init__(self, file_path: Path | str):
        self.path = str(file_path)

    def read(self) -> str:
        return Path(self.path).read_text()
