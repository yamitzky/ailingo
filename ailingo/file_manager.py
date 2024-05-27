from pathlib import Path


class FileManager:
    def read_text_file(self, file_path: str) -> str:
        """
        Read a text file from the specified path.
        """
        return Path(file_path).read_text()

    def check_exists(self, file_path: str) -> bool:
        """
        Check if the file exists.
        """
        return Path(file_path).exists()

    def save_text_file(self, file_path: str, content: str) -> None:
        """
        Save a text file to the specified path.
        """
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(file_path).write_text(content)

    def generate_path_by_pattern(
        self, input_path_str: str, output_pattern: str, **context
    ) -> str:
        """
        Generate the output file path from the input file path and pattern.
        """
        input_path = Path(input_path_str)
        return output_pattern.format(
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

    def generate_path_by_replacement(
        self, input_path: str, source: str, target: str
    ) -> str | None:
        """
        Returns the path with the source replaced by the target if the source is part of the file path.
        Returns None if the source is not found in the file path.
        """
        path = Path(input_path)
        parts = path.parts

        # Check if the source is a part of the directory structure
        if source in parts:
            new_parts = [target if part == source else part for part in parts]
            return str(Path(*new_parts))

        # Check if the source is part of the file name stem
        stem_parts = path.name.split(".")
        if source in stem_parts:
            stem_parts = [target if part == source else part for part in stem_parts]
            new_name = ".".join(stem_parts)
            return str(path.with_name(new_name))

        return None
