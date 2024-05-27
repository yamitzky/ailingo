import pytest
from ailingo.file_manager import FileManager


@pytest.fixture
def file_manager():
    return FileManager()


def test_read_text_file(tmp_path):
    file_path = tmp_path / "test.txt"
    content = "Hello, world!"
    file_path.write_text(content)

    file_manager = FileManager()
    read_content = file_manager.read_text_file(str(file_path))

    assert read_content == content


def test_check_exists(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.touch()

    file_manager = FileManager()
    exists = file_manager.check_exists(str(file_path))

    assert exists


def test_save_text_file(tmp_path):
    file_path = tmp_path / "test.txt"
    content = "Hello, world!"

    file_manager = FileManager()
    file_manager.save_text_file(str(file_path), content)

    assert file_path.read_text() == content


def test_generate_output_path():
    file_manager = FileManager()
    input_path = "dir/test.txt"
    output_pattern = "{parent}/{stem}.translated{suffix}"

    output_path = file_manager.generate_path_by_pattern(input_path, output_pattern)
    assert output_path == "dir/test.translated.txt"

    input_path = "/path/to/en/my_document.txt"
    output_pattern = "{parents[1]}/{target}/{name}"
    output_path = file_manager.generate_path_by_pattern(
        input_path, output_pattern, target="ja"
    )
    assert output_path == "/path/to/ja/my_document.txt"


def test_auto_generate_output_path():
    file_manager = FileManager()
    input_path = "test/document.en.txt"
    source = "en"
    target = "ja"
    expected_output_path = "test/document.ja.txt"
    assert (
        file_manager.generate_path_by_replacement(input_path, source, target)
        == expected_output_path
    )

    file_manager = FileManager()
    input_path = "locales/en/LC_MESSAGES/message.po"
    source = "en"
    target = "ja"
    expected_output_path = "locales/ja/LC_MESSAGES/message.po"
    assert (
        file_manager.generate_path_by_replacement(input_path, source, target)
        == expected_output_path
    )


def test_auto_generate_output_path_is_not_possible():
    # no parts to replace
    file_manager = FileManager()
    input_path = "test/document.txt"
    source = "en"
    target = "ja"
    assert file_manager.generate_path_by_replacement(input_path, source, target) is None

    # not enough parts to replace
    file_manager = FileManager()
    input_path = "test/en-US/document.txt"
    source = "en"
    target = "ja"
    assert file_manager.generate_path_by_replacement(input_path, source, target) is None
