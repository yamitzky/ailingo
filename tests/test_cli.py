from unittest.mock import MagicMock, call, patch

from typer.testing import CliRunner

from transpa.cli import app

runner = CliRunner()


@patch("transpa.cli.Translator")
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


@patch("transpa.cli.Translator")
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


@patch("transpa.cli.Translator")
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
