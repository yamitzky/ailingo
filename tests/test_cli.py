import logging
from unittest.mock import MagicMock, call, patch

from ailingo.cli import app
from ailingo.translator import Translator
from typer.testing import CliRunner

runner = CliRunner()


def mock_subprocess_run(*args, **kwargs):
    with open(args[0][1], "w") as f:
        f.write("Edited content for translation.")


def mock_translate(*args, **kwargs):
    with open(kwargs["output_pattern"], "w") as f:
        f.write("Translated content.")


@patch("ailingo.cli.Translator")
def test_translate_command(mock_translator):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            "test.txt",
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
        file_path="test.txt",
        source_language=None,
        target_language="fr",
        output_pattern="{parent}/{stem}.fr{suffix}",
        overwrite=False,
        dryrun=False,
        request=None,
        quiet=False,
    )
    assert mock_instance.translate.call_count == 1
    mock_translator.assert_called_once_with(model_name="gpt-4o")


@patch("ailingo.cli.Translator")
def test_translate_multiple_files(mock_translator):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            "test.txt",
            "test2.txt",
            "-t",
            "fr,ja",
            "-m",
            "gemini-1.5-pro",
            "-o",
            "{parent}/{stem}{target}{suffix}",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_has_calls(
        [
            call(
                file_path="test.txt",
                source_language=None,
                target_language="fr",
                output_pattern="{parent}/{stem}{target}{suffix}",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
            call(
                file_path="test2.txt",
                source_language=None,
                target_language="fr",
                output_pattern="{parent}/{stem}{target}{suffix}",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
            call(
                file_path="test.txt",
                source_language=None,
                target_language="ja",
                output_pattern="{parent}/{stem}{target}{suffix}",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
            call(
                file_path="test2.txt",
                source_language=None,
                target_language="ja",
                output_pattern="{parent}/{stem}{target}{suffix}",
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
        ],
        any_order=True,
    )
    assert mock_instance.translate.call_count == 4
    mock_translator.assert_called_once_with(model_name="gemini-1.5-pro")


@patch("ailingo.cli.Translator")
def test_rewrite_mode(mock_translator):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    result = runner.invoke(
        app,
        [
            "test.txt",
            "test2.txt",
            "-s",
            "en",
        ],
    )

    assert result.exit_code == 0
    mock_instance.translate.assert_has_calls(
        [
            call(
                file_path="test.txt",
                source_language="en",
                target_language=None,
                output_pattern=None,
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
            call(
                file_path="test2.txt",
                source_language="en",
                target_language=None,
                output_pattern=None,
                overwrite=False,
                dryrun=False,
                request=None,
                quiet=False,
            ),
        ],
        any_order=True,
    )
    assert mock_instance.translate.call_count == 2


@patch.object(Translator, "translate", side_effect=mock_translate)
@patch("ailingo.cli.subprocess.run", side_effect=mock_subprocess_run)
def test_translate_edit_mode(mock_translator, mock_run_editor, tmp_path):
    result = runner.invoke(app, ["-e"])
    assert result.exit_code == 0
    assert "Translated content." in result.output

    result = runner.invoke(app, ["-e", "-o", str(tmp_path / "output.txt")])
    assert result.exit_code == 0
    assert "Translated content." not in result.output
    with open(tmp_path / "output.txt") as f:
        assert f.read() == "Translated content."


def test_translate_invalid_language_option():
    result = runner.invoke(app, ["-e", "-t", "fr,de"])
    assert result.exit_code == 2
    assert (
        "Multiple target languages cannot be specified in edit mode." in result.output
    )


def test_translate_edit_mode_with_file_argument(tmp_path):
    result = runner.invoke(app, [str(tmp_path), "-e"])
    assert result.exit_code == 2
    assert "File paths cannot be specified in edit mode." in result.output


@patch("ailingo.cli.subprocess.run", side_effect=mock_subprocess_run)
def test_translate_editor_no_changes(mock_run):
    with patch("os.path.getsize", return_value=0):
        result = runner.invoke(app, ["-e"])
    assert result.exit_code == 1
    assert "No changes made. Exiting..." in result.output


@patch("ailingo.cli.Translator")
def test_debug_mode(mock_translator, caplog):
    mock_instance = MagicMock()
    mock_translator.return_value = mock_instance

    with caplog.at_level(logging.DEBUG):
        runner.invoke(app, ["translate", "dummy.txt", "--target", "en"])
    assert "DEBUG" not in caplog.text

    with caplog.at_level(logging.DEBUG):
        runner.invoke(app, ["--debug", "translate", "dummy.txt", "--target", "en"])
    assert "DEBUG" in caplog.text
