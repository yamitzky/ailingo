from unittest.mock import MagicMock, call, patch

import pytest
from ailingo.file_manager import FileManager
from ailingo.llm import LLM
from ailingo.translator import Translator


@pytest.fixture
def mock_file_manager():
    return MagicMock(spec=FileManager)


@pytest.fixture
def mock_llm():
    return MagicMock(spec=LLM)


@pytest.fixture
def translator(mock_file_manager, mock_llm):
    return Translator(model_name="gpt-4o", file_manager=mock_file_manager, llm=mock_llm)


def test_translate_dryrun(translator: Translator, mock_file_manager, mock_llm):
    translator.translate(
        file_path="test.txt",
        target_language="fr",
        output_pattern="{parent}/{stem}.fr{suffix}",
        dryrun=True,
    )

    mock_llm.completion.assert_not_called()
    mock_file_manager.read_text_file.assert_not_called()
    mock_file_manager.save_text_file.assert_not_called()


def test_translate_new_file(translator: Translator, mock_file_manager, mock_llm):
    mock_file_manager.check_exists.return_value = False
    mock_file_manager.read_text_file.return_value = "Hello, world!"
    mock_file_manager.generate_path_by_pattern.return_value = "test.fr.txt"
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        file_path="test.txt",
        target_language="fr",
        output_pattern="{parent}/{stem}.fr{suffix}",
        overwrite=False,
    )

    mock_llm.completion.assert_called_once_with(
        [
            {
                "role": "system",
                "content": "You are a translator that translates files. "
                "Please translate the content of the file provided by the user.\n"
                "Only output the translation result. Do not output any related comments and code blocks.\n"
                "Please follow the information below for reference.\n"
                "- Target language code: fr\n"
                "- File extension: .txt",
            },
            {
                "role": "user",
                "content": "User provided text:\n----------\nHello, world!",
            },
        ],
    )
    mock_file_manager.save_text_file.assert_called_once_with(
        "test.fr.txt", "Bonjour, le monde!"
    )


def translate_with_source(translator: Translator, mock_file_manager, mock_llm):
    mock_file_manager.check_exists.return_value = False
    mock_file_manager.read_text_file.return_value = "Hello, world!"
    mock_file_manager.generate_path_by_pattern.return_value = "test.fr.txt"
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        file_path="test.txt",
        source_language="en",
        target_language="fr",
        output_pattern="{parent}/{stem}.fr{suffix}",
        overwrite=False,
    )

    mock_llm.completion.assert_called_once_with(
        [
            {
                "role": "system",
                "content": "You are a translator that translates files. "
                "Please translate the content of the file provided by the user.\n"
                "Only output the translation result. Do not output any related comments and code blocks.\n"
                "Please follow the information below for reference.\n"
                "- Source language code: en\n"
                "- Target language code: fr\n"
                "- File extension: .txt\n",
            },
            {
                "role": "user",
                "content": "User provided text:\n----------\nHello, world!",
            },
        ],
    )
    mock_file_manager.save_text_file.assert_called_once_with(
        "test.fr.txt", "Bonjour, le monde!"
    )


def test_translate_no_overwrite(translator: Translator, mock_file_manager, mock_llm):
    mock_file_manager.check_exists.return_value = True

    with patch("rich.prompt.Confirm.ask", return_value=False):
        translator.translate(
            file_path="test.txt",
            target_language="fr",
            output_pattern="{parent}/{stem}.fr{suffix}",
            overwrite=False,
        )

    mock_llm.completion.assert_not_called()
    mock_file_manager.read_text_file.assert_not_called()
    mock_file_manager.save_text_file.assert_not_called()


def test_translate_overwrite(translator: Translator, mock_file_manager, mock_llm):
    mock_file_manager.check_exists.return_value = True
    mock_file_manager.read_text_file.side_effect = lambda file_path: (
        "Hello, world!"
        if file_path == "test.txt"
        else "Bonjour, le monde(existing file)"
    )
    mock_file_manager.generate_path_by_pattern.return_value = "test.fr.txt"
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        file_path="test.txt",
        target_language="fr",
        output_pattern="{parent}/{stem}.fr{suffix}",
        overwrite=True,
    )

    mock_file_manager.read_text_file.assert_has_calls(
        [call("test.fr.txt"), call("test.txt")]
    )
    mock_llm.completion.assert_called_once_with(
        [
            {
                "role": "system",
                "content": "You are a translator that translates files. Please translate "
                "the content of the file provided by the user.\n"
                "Only output the translation result. Do not output any related comments and code blocks.\n"
                "Please follow the information below for reference.\n"
                "- Target language code: fr\n"
                "- File extension: .txt\n"
                "Also, some content has been previously translated. "
                "Please use the original content as much as possible, "
                "and only change and translate the parts that differ from the text provided by the user.\n"
                "Bonjour, le monde(existing file)",
            },
            {
                "role": "user",
                "content": "User provided text:\n----------\nHello, world!",
            },
        ],
    )
    mock_file_manager.save_text_file.assert_called_once_with(
        "test.fr.txt", "Bonjour, le monde!"
    )


def test_auto_generate_output_path(translator: Translator, mock_file_manager, mock_llm):
    mock_file_manager.check_exists.return_value = False
    mock_file_manager.read_text_file.return_value = "Hello, world!"
    mock_file_manager.generate_path_by_pattern.return_value = "test.en.fr.txt"
    mock_file_manager.generate_path_by_replacement.return_value = "test.fr.txt"
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        file_path="test.en.txt",
        source_language="en",
        target_language="fr",
        overwrite=False,
        output_pattern=None,
    )

    mock_file_manager.save_text_file.assert_called_once_with(
        "test.fr.txt", "Bonjour, le monde!"
    )


def test_auto_generate_fallback(translator: Translator, mock_file_manager, mock_llm):
    mock_file_manager.check_exists.return_value = False
    mock_file_manager.read_text_file.return_value = "Hello, world!"
    mock_file_manager.generate_path_by_pattern.return_value = "test.fr.txt"
    mock_file_manager.generate_path_by_replacement.return_value = None
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        file_path="test.en.txt",
        source_language="en",
        target_language="fr",
        overwrite=False,
        output_pattern=None,
    )

    mock_file_manager.save_text_file.assert_called_once_with(
        "test.fr.txt", "Bonjour, le monde!"
    )


def test_translate_with_request(translator: Translator, mock_file_manager, mock_llm):
    mock_file_manager.check_exists.return_value = False
    mock_file_manager.read_text_file.return_value = "Hello, world!"
    mock_file_manager.generate_path_by_pattern.return_value = "test.fr.txt"
    mock_llm.completion.return_value = "Bonjour, world!"

    translator.translate(
        file_path="test.txt",
        target_language="fr",
        output_pattern="{parent}/{stem}.fr{suffix}",
        overwrite=False,
        request="Do not translate the word 'world'.",
    )

    mock_llm.completion.assert_called_once_with(
        [
            {
                "role": "system",
                "content": "You are a translator that translates files. "
                "Please translate the content of the file provided by the user.\n"
                "Only output the translation result. Do not output any related comments and code blocks.\n"
                "Please follow the information below for reference.\n"
                "- Target language code: fr\n"
                "- File extension: .txt\n"
                "- Additional request: Do not translate the word 'world'.",
            },
            {
                "role": "user",
                "content": "User provided text:\n----------\nHello, world!",
            },
        ],
    )
    mock_file_manager.save_text_file.assert_called_once_with(
        "test.fr.txt", "Bonjour, world!"
    )


def test_rewrite(translator: Translator, mock_file_manager, mock_llm):
    mock_file_manager.check_exists.return_value = True
    mock_file_manager.read_text_file.return_value = "Hello, world!"
    mock_llm.completion.return_value = "HELLO, WORLD!"

    translator.translate(file_path="test.txt", overwrite=True)

    mock_llm.completion.assert_called_once_with(
        [
            {
                "role": "system",
                "content": "You are a writer who rewrites text.\n"
                "Please rewrite the provided text to make it more natural without changing the original meaning.\n"
                "As a native speaker, correct any spelling, grammar, or terminology errors.\n"
                "Only output the result. Do not output any related comments and code blocks.\n"
                "Never translate. Don't change the language. Please respect the original language.\n"
                "Please follow the information below for reference.\n"
                "- File extension: .txt\n"
                "Also, some content has been previously translated. "
                "Please use the original content as much as possible, and only change and translate the parts "
                "that differ from the text provided by the user.\n"
                "Hello, world!",
            },
            {
                "role": "user",
                "content": "User provided text:\n----------\nHello, world!",
            },
        ],
    )
    mock_file_manager.save_text_file.assert_called_once_with(
        "test.txt", "HELLO, WORLD!"
    )
