import logging
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from typer.testing import CliRunner

from ailingo.cli import app
from ailingo.input_source.editor_source import EditorInputSource
from ailingo.input_source.file_source import FileInputSource
from ailingo.input_source.url_source import UrlInputSource
from ailingo.output_source.console_source import ConsoleOutputSource
from ailingo.output_source.file_source import FileOutputSource

runner = CliRunner()


def mock_subprocess_run(*args, **kwargs):
    with open(args[0][1], "w") as f:
        f.write("Edited content for translation.")


def mock_translate(*args, **kwargs):
    with open(kwargs["output_pattern"], "w") as f:
        f.write("Translated content.")


@pytest.fixture
def test_file(tmp_path):
    file_path = tmp_path / "test.txt"
    with open(file_path, "w") as f:
        f.write("Test content.")
    return file_path


@pytest.fixture
def test_file_2(tmp_path):
    file_path = tmp_path / "test2.txt"
    with open(file_path, "w") as f:
        f.write("Test content.")
    return file_path


@pytest.fixture
def test_md(tmp_path):
    file_path = tmp_path / "test.md"
    with open(file_path, "w") as f:
        f.write("Test content.")
    return file_path


@patch("ailingo.cli.Translator")
def test_translate_command(mock_translator, test_file: Path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            "-t",
            "fr",
            "-m",
            "gpt-4o",
            "-o",
            "{parent}/{stem}.fr{suffix}",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(test_file)),
        output_source=FileOutputSource(str(test_file.parent / "test.fr.txt")),
        source_language=None,
        target_language="fr",
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
        stream=False,
    )
    assert mock_instance.translate.call_count == 1


@patch("ailingo.cli.Translator")
def test_translate_with_stream(mock_translator, test_file: Path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            "-t",
            "fr",
            "--stream",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(test_file)),
        output_source=FileOutputSource(str(test_file.parent / "test.fr.txt")),
        source_language=None,
        target_language="fr",
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
        stream=True,
    )
    assert mock_instance.translate.call_count == 1


@patch("ailingo.cli.Translator")
def test_model_name_from_environment_variable(mock_translator, test_file: Path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            "-t",
            "fr",
        ],
        env={"AILINGO_MODEL": "model-from-cli"},
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once()
    mock_translator.assert_called_once_with(model_name="model-from-cli")


@patch("ailingo.cli.Translator")
def test_translate_multiple_files(mock_translator, test_file: Path, test_file_2: Path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            str(test_file_2),
            "-t",
            "fr,ja",
            "-m",
            "gemini-1.5-pro",
            "-o",
            "{parent}/{stem}.{target}{suffix}",
        ],
    )

    assert result.exit_code == 0
    assert mock_instance.translate.call_count == 4
    mock_instance.translate.assert_has_calls(
        [
            call(
                input_source=FileInputSource(str(test_file)),
                output_source=FileOutputSource(str(test_file.parent / "test.fr.txt")),
                source_language=None,
                target_language="fr",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
                stream=False,
            ),
            call(
                input_source=FileInputSource(str(test_file_2)),
                output_source=FileOutputSource(
                    str(test_file_2.parent / "test2.fr.txt")
                ),
                source_language=None,
                target_language="fr",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
                stream=False,
            ),
            call(
                input_source=FileInputSource(str(test_file)),
                output_source=FileOutputSource(str(test_file.parent / "test.ja.txt")),
                source_language=None,
                target_language="ja",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
                stream=False,
            ),
            call(
                input_source=FileInputSource(str(test_file_2)),
                output_source=FileOutputSource(
                    str(test_file_2.parent / "test2.ja.txt")
                ),
                source_language=None,
                target_language="ja",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
                stream=False,
            ),
        ],
        any_order=True,
    )


@patch("ailingo.cli.Translator")
def test_rewrite_mode(mock_translator, test_file: Path, test_file_2: Path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            str(test_file_2),
            "-s",
            "en",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_has_calls(
        [
            call(
                input_source=FileInputSource(str(test_file)),
                output_source=FileOutputSource(str(test_file_2.parent / "test.txt")),
                source_language="en",
                target_language=None,
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
                stream=False,
            ),
            call(
                input_source=FileInputSource(str(test_file_2)),
                output_source=FileOutputSource(str(test_file_2.parent / "test2.txt")),
                source_language="en",
                target_language=None,
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
                stream=False,
            ),
        ],
        any_order=True,
    )
    assert mock_instance.translate.call_count == 2


@patch("ailingo.cli.Translator")
def test_edit_mode(mock_translator):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(app, ["-e"])
    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=EditorInputSource(),
        output_source=ConsoleOutputSource(),
        source_language=None,
        target_language=None,
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
        stream=False,
    )


@patch("ailingo.cli.Translator")
def test_edit_mode_with_output_file(mock_translator, tmp_path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(app, ["-e", "-o", str(tmp_path / "output.txt")])
    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=EditorInputSource(),
        output_source=FileOutputSource(str(tmp_path / "output.txt")),
        source_language=None,
        target_language=None,
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
        stream=False,
    )


@patch("ailingo.cli.Translator")
def test_edit_mode_with_console_output(mock_translator):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(app, ["-e", "-o", "-"])
    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=EditorInputSource(),
        output_source=ConsoleOutputSource(markdown=False),
        source_language=None,
        target_language=None,
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
        stream=False,
    )


@patch("ailingo.cli.Translator")
def test_translate_default_output(mock_translator, test_file):
    """Test translating a single file with the default output pattern."""
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            "-t",
            "fr",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(test_file)),
        output_source=FileOutputSource(str(test_file.parent / "test.fr.txt")),
        source_language=None,
        target_language="fr",
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
        stream=False,
    )
    assert mock_instance.translate.call_count == 1


@patch("ailingo.cli.Translator")
def test_translate_with_console_output(mock_translator, test_file):
    """Test translating a single file with console output."""
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            "-t",
            "fr",
            "-o",
            "-",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(test_file)),
        output_source=ConsoleOutputSource(markdown=False),
        source_language=None,
        target_language="fr",
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
        stream=False,
    )
    assert mock_instance.translate.call_count == 1


@patch("ailingo.cli.Translator")
def test_markdown_suffixed_input_file(mock_translator, test_md: Path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(app, [str(test_md), "-o", "-"])

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(test_md)),
        output_source=ConsoleOutputSource(markdown=True),
        source_language=None,
        target_language=None,
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
        stream=False,
    )
    assert mock_instance.translate.call_count == 1


def test_translate_invalid_language_option():
    result = runner.invoke(app, ["-e", "-t", "fr,de"])
    assert result.exit_code == 2
    assert (
        "Multiple target languages cannot be specified in edit mode." in result.output
    )


def test_translate_edit_mode_with_file_argument(test_file):
    result = runner.invoke(app, [str(test_file), "-e"])
    assert result.exit_code == 2
    assert "File paths cannot be specified in edit mode." in result.output


@patch("ailingo.cli.Translator")
def test_debug_mode(mock_translator, caplog, test_file):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    with caplog.at_level(logging.INFO):
        runner.invoke(app, [str(test_file), "--target", "en"])
    assert "DEBUG" not in caplog.text

    with caplog.at_level(logging.DEBUG):
        runner.invoke(app, ["--debug", str(test_file), "--target", "en"])
    assert "DEBUG" in caplog.text


@patch("ailingo.cli.Translator")
def test_translate_url(mock_translator, tmp_path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            "-u",
            "https://example.com",
            "-t",
            "fr",
            "-m",
            "gpt-4o",
            "-o",
            str(tmp_path / "output.fr.txt"),
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=UrlInputSource("https://example.com"),
        output_source=FileOutputSource(str(tmp_path / "output.fr.txt")),
        source_language=None,
        target_language="fr",
        overwrite=False,
        dryrun=False,
        request="Original text is extracted from a website. Convert it to markdown.",
        quiet=False,
        stream=False,
    )
    assert mock_instance.translate.call_count == 1
    mock_translator.assert_called_once_with(model_name="gpt-4o")


@patch("ailingo.cli.Translator")
def test_translate_with_request(mock_translator, test_file: Path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            "-t",
            "ja",
            "-r",
            "Translate to casual Japanese",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(test_file)),
        output_source=FileOutputSource(str(test_file.parent / "test.ja.txt")),
        source_language=None,
        target_language="ja",
        overwrite=False,
        dryrun=False,
        request="Translate to casual Japanese",
        quiet=False,
        stream=False,
    )


@patch("ailingo.cli.Translator")
def test_translate_with_overwrite(mock_translator, test_file: Path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            "-t",
            "fr",
            "-y",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(test_file)),
        output_source=FileOutputSource(str(test_file.parent / "test.fr.txt")),
        source_language=None,
        target_language="fr",
        overwrite=True,
        dryrun=False,
        request=None,
        quiet=False,
        stream=False,
    )


@patch("ailingo.cli.Translator")
def test_translate_with_dryrun(mock_translator, test_file: Path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            str(test_file),
            "-t",
            "de",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(test_file)),
        output_source=FileOutputSource(str(test_file.parent / "test.de.txt")),
        source_language=None,
        target_language="de",
        overwrite=False,
        dryrun=True,
        request=None,
        quiet=False,
        stream=False,
    )
