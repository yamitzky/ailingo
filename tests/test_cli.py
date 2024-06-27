import logging
from unittest.mock import MagicMock, call, patch

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


@patch("ailingo.cli.Translator")
def test_translate_command(mock_translator, tmp_path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance
    with open(tmp_path / "test.txt", "w") as f:
        f.write("Test content.")

    result = runner.invoke(
        app,
        [
            str(tmp_path / "test.txt"),
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
        input_source=FileInputSource(str(tmp_path / "test.txt")),
        output_source=FileOutputSource(str(tmp_path / "test.fr.txt")),
        source_language=None,
        target_language="fr",
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
    )
    assert mock_instance.translate.call_count == 1
    mock_translator.assert_called_once_with(model_name="gpt-4o")


@patch("ailingo.cli.Translator")
def test_model_name_from_environment_variable(mock_translator, tmp_path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    with open(tmp_path / "test.txt", "w") as f:
        f.write("Test content.")

    result = runner.invoke(
        app,
        [
            str(tmp_path / "test.txt"),
            "-t",
            "fr",
        ],
        env={"AILINGO_MODEL": "model-from-cli"},
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once()
    mock_translator.assert_called_once_with(model_name="model-from-cli")


@patch("ailingo.cli.Translator")
def test_translate_multiple_files(mock_translator, tmp_path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance
    with open(tmp_path / "test.txt", "w") as f:
        f.write("Test content.")
    with open(tmp_path / "test2.txt", "w") as f:
        f.write("Test content.")

    result = runner.invoke(
        app,
        [
            str(tmp_path / "test.txt"),
            str(tmp_path / "test2.txt"),
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
                input_source=FileInputSource(str(tmp_path / "test.txt")),
                output_source=FileOutputSource(str(tmp_path / "test.fr.txt")),
                source_language=None,
                target_language="fr",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
            call(
                input_source=FileInputSource(str(tmp_path / "test2.txt")),
                output_source=FileOutputSource(str(tmp_path / "test2.fr.txt")),
                source_language=None,
                target_language="fr",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
            call(
                input_source=FileInputSource(str(tmp_path / "test.txt")),
                output_source=FileOutputSource(str(tmp_path / "test.ja.txt")),
                source_language=None,
                target_language="ja",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
            call(
                input_source=FileInputSource(str(tmp_path / "test2.txt")),
                output_source=FileOutputSource(str(tmp_path / "test2.ja.txt")),
                source_language=None,
                target_language="ja",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
        ],
        any_order=True,
    )
    mock_translator.assert_called_once_with(model_name="gemini-1.5-pro")


@patch("ailingo.cli.Translator")
def test_rewrite_mode(mock_translator, tmp_path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance
    with open(tmp_path / "test.txt", "w") as f:
        f.write("Test content.")
    with open(tmp_path / "test2.txt", "w") as f:
        f.write("Test content.")

    result = runner.invoke(
        app,
        [
            str(tmp_path / "test.txt"),
            str(tmp_path / "test2.txt"),
            "-s",
            "en",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_has_calls(
        [
            call(
                input_source=FileInputSource(str(tmp_path / "test.txt")),
                output_source=FileOutputSource(str(tmp_path / "test.txt")),
                source_language="en",
                target_language=None,
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
            call(
                input_source=FileInputSource(str(tmp_path / "test2.txt")),
                output_source=FileOutputSource(str(tmp_path / "test2.txt")),
                source_language="en",
                target_language=None,
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
        ],
        any_order=True,
    )
    assert mock_instance.translate.call_count == 2


@patch("ailingo.cli.Translator")
def test_edit_mode(mock_translator, tmp_path):
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
    )


@patch("ailingo.cli.Translator")
def test_translate_default_output(mock_translator, tmp_path):
    """Test translating a single file with the default output pattern."""
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance
    with open(tmp_path / "test.txt", "w") as f:
        f.write("Test content.")

    result = runner.invoke(
        app,
        [
            str(tmp_path / "test.txt"),
            "-t",
            "fr",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(tmp_path / "test.txt")),
        output_source=FileOutputSource(str(tmp_path / "test.fr.txt")),
        source_language=None,
        target_language="fr",
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
    )
    assert mock_instance.translate.call_count == 1


@patch("ailingo.cli.Translator")
def test_translate_with_console_output(mock_translator, tmp_path):
    """Test translating a single file with console output."""
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance
    with open(tmp_path / "test.txt", "w") as f:
        f.write("Test content.")

    result = runner.invoke(
        app,
        [
            str(tmp_path / "test.txt"),
            "-t",
            "fr",
            "-o",
            "-",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(tmp_path / "test.txt")),
        output_source=ConsoleOutputSource(markdown=False),
        source_language=None,
        target_language="fr",
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
    )
    assert mock_instance.translate.call_count == 1


@patch("ailingo.cli.Translator")
def test_markdown_suffixed_input_file(mock_translator, tmp_path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance
    with open(tmp_path / "test.md", "w") as f:
        f.write("Test content.")

    result = runner.invoke(app, [str(tmp_path / "test.md"), "-o", "-"])

    assert result.exit_code == 0
    mock_instance.translate.assert_called_once_with(
        input_source=FileInputSource(str(tmp_path / "test.md")),
        output_source=ConsoleOutputSource(markdown=True),
        source_language=None,
        target_language=None,
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
    )
    assert mock_instance.translate.call_count == 1


def test_translate_invalid_language_option():
    result = runner.invoke(app, ["-e", "-t", "fr,de"])
    assert result.exit_code == 2
    assert (
        "Multiple target languages cannot be specified in edit mode." in result.output
    )


def test_translate_edit_mode_with_file_argument(tmp_path):
    with open(tmp_path / "test.txt", "w") as f:
        f.write("Test content.")
    result = runner.invoke(app, [str(tmp_path / "test.txt"), "-e"])
    assert result.exit_code == 2
    assert "File paths cannot be specified in edit mode." in result.output


@patch("ailingo.cli.Translator")
def test_debug_mode(mock_translator, caplog, tmp_path):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance
    with open(tmp_path / "dummy.txt", "w") as f:
        f.write("Test content.")

    with caplog.at_level(logging.INFO):
        runner.invoke(app, [str(tmp_path / "dummy.txt"), "--target", "en"])
    assert "DEBUG" not in caplog.text

    with caplog.at_level(logging.DEBUG):
        runner.invoke(app, ["--debug", str(tmp_path / "dummy.txt"), "--target", "en"])
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
    )
    assert mock_instance.translate.call_count == 1
    mock_translator.assert_called_once_with(model_name="gpt-4o")
