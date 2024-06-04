import os
import tempfile
from unittest import mock
from unittest.mock import MagicMock

import pytest

from ailingo.input_source.editor_source import EditorInputSource


def test_read_dryrun():
    editor_source = EditorInputSource(dryrun=True)
    assert editor_source.read() == ""


@mock.patch("ailingo.input_source.editor_source._run_editor")
def test_read(mock_run_editor: MagicMock):
    editor_source = EditorInputSource()
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as f:
        f.write("test")
        f.seek(0)
        with mock.patch(
            "ailingo.input_source.editor_source.tempfile.NamedTemporaryFile",
            return_value=f,
        ):
            assert editor_source.read() == "test"
    mock_run_editor.assert_called_once()


@mock.patch("ailingo.input_source.editor_source.os.path.getsize", return_value=100)
@mock.patch("ailingo.input_source.editor_source.subprocess.run")
def test_run_editor(mock_subprocess_run: MagicMock, mock_os_path_getsize: MagicMock):
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as f:
        original_environ = dict(os.environ)
        os.environ["EDITOR"] = "vim"
        try:
            with mock.patch(
                "ailingo.input_source.editor_source.tempfile.NamedTemporaryFile",
                return_value=f,
            ):
                _ = EditorInputSource().read()
                mock_subprocess_run.assert_called_once_with(["vim", f.name], check=True)
        finally:
            os.environ.clear()
            os.environ.update(original_environ)


@mock.patch(
    "ailingo.input_source.editor_source.subprocess.run", side_effect=FileNotFoundError
)
def test_run_editor_not_found(mock_subprocess_run: MagicMock):
    with pytest.raises(Exception) as e:
        _ = EditorInputSource().read()
    assert str(e.value) == "Editor not found"


@mock.patch("ailingo.input_source.editor_source.os.path.getsize", return_value=0)
@mock.patch("ailingo.input_source.editor_source.subprocess.run")
def test_run_editor_no_changes(
    mock_subprocess_run: MagicMock, mock_os_path_getsize: MagicMock
):
    with pytest.raises(Exception) as e:
        _ = EditorInputSource().read()
    assert str(e.value) == "No changes made"
