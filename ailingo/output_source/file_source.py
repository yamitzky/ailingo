from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class FileOutputSource:
    path: str

    def __init__(self, path: str | Path):
        self.path = str(path)

    def write(self, text: str):
        Path(self.path).write_text(text)

    def write_stream(self, text: Iterable[str]):
        with Path(self.path).open("w") as f:
            for chunk in text:
                f.write(chunk)

    def read(self) -> str:
        return Path(self.path).read_text()

    def exists(self) -> bool:
        return Path(self.path).exists()

    @property
    def readable(self) -> bool:
        return self.exists()

    @staticmethod
    def from_pattern(
        input_path_str: str, output_pattern: str, **context
    ) -> "FileOutputSource":
        """
        Generate the output file path from the input file path and pattern.
        """
        input_path = Path(input_path_str)
        return FileOutputSource(
            output_pattern.format(
                drive=input_path.drive,
                root=input_path.root,
                anchor=input_path.anchor,
                parents=input_path.parents,
                parent=input_path.parent,
                name=input_path.name,
                suffix=input_path.suffix,
                suffixes=input_path.suffixes,
                stem=input_path.stem,
                **context,
            )
        )

    @staticmethod
    def from_replacement(
        input_path: str, source: str, target: str
    ) -> "FileOutputSource":
        """
        Returns the path with the source replaced by the target if the source is part of the file path.
        Returns None if the source is not found in the file path.
        """
        path = Path(input_path)
        parts = path.parts

        # Check if the source is a part of the directory structure
        if source in parts:
            new_parts = [target if part == source else part for part in parts]
            return FileOutputSource(str(Path(*new_parts)))

        # Check if the source is part of the file name stem
        stem_parts = path.name.split(".")
        if source in stem_parts:
            stem_parts = [target if part == source else part for part in stem_parts]
            new_name = ".".join(stem_parts)
            return FileOutputSource(str(path.with_name(new_name)))

        raise ValueError(f"Source {source} not found in file path {input_path}")
