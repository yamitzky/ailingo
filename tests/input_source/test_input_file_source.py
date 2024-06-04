from pathlib import Path

from ailingo.input_source.file_source import FileInputSource


def test_file_source(tmp_path):
    file_path = tmp_path / "test.txt"
    file_content = "This is a test file.\n"
    with open(file_path, "w") as f:
        f.write(file_content)

    file_source = FileInputSource(file_path)
    assert file_source.read() == file_content
