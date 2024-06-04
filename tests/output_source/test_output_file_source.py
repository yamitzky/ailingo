from pathlib import Path

import pytest

from ailingo.output_source.file_source import FileOutputSource


def test_check_exists(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.touch()

    output_source = FileOutputSource(file_path)
    assert output_source.exists()

    output_source = FileOutputSource(tmp_path / "test2.txt")
    assert not output_source.exists()


def test_save_text_file(tmp_path: Path):
    file_path = tmp_path / "test.txt"
    content = "Hello, world!"

    output_source = FileOutputSource(file_path)
    output_source.write(content)

    assert file_path.read_text() == content


def test_generate_output_path():
    input_path = "dir/test.txt"
    output_pattern = "{parent}/{stem}.translated{suffix}"

    output_path = FileOutputSource.from_pattern(input_path, output_pattern)
    assert output_path.path == "dir/test.translated.txt"

    input_path = "/path/to/en/my_document.txt"
    output_pattern = "{parents[1]}/{target}/{name}"
    output_path = FileOutputSource.from_pattern(input_path, output_pattern, target="ja")
    assert output_path.path == "/path/to/ja/my_document.txt"


def test_auto_generate_output_path():
    input_path = "test/document.en.txt"
    source = "en"
    target = "ja"
    expected_output_path = "test/document.ja.txt"
    assert (
        FileOutputSource.from_replacement(input_path, source, target).path
        == expected_output_path
    )

    input_path = "locales/en/LC_MESSAGES/message.po"
    source = "en"
    target = "ja"
    expected_output_path = "locales/ja/LC_MESSAGES/message.po"
    assert (
        FileOutputSource.from_replacement(input_path, source, target).path
        == expected_output_path
    )


def test_auto_generate_output_path_is_not_possible():
    # no parts to replace
    input_path = "test/document.txt"
    source = "en"
    target = "ja"
    with pytest.raises(ValueError):
        FileOutputSource.from_replacement(input_path, source, target)

    # not enough parts to replace
    input_path = "test/en-US/document.txt"
    source = "en"
    target = "ja"

    with pytest.raises(ValueError):
        FileOutputSource.from_replacement(input_path, source, target)
