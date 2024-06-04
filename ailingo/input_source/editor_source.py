import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

err_console = Console(stderr=True)


@dataclass
class EditorInputSource:
    path: str = "(temporary file)"

    def read(self) -> str:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as f:
            self.path = f.name
            _run_editor(f.name)
            text = Path(f.name).read_text()
        return text


def _run_editor(file_path: str):
    editor = os.getenv("EDITOR", "vi")
    try:
        subprocess.run([editor, file_path], check=True)
    except FileNotFoundError:
        err_console.print(f"Editor '{editor}' not found. Please set a default editor.")
        raise Exception("Editor not found")

    if os.path.getsize(file_path) == 0:
        err_console.print("No changes made. Exiting...")
        raise Exception("No changes made")
