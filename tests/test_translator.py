from unittest.mock import MagicMock, patch

import pytest

from ailingo.input_source.file_source import FileInputSource
from ailingo.llm import LLM
from ailingo.output_source.file_source import FileOutputSource
from ailingo.translator import Translator


@pytest.fixture
def mock_llm():
    return MagicMock(spec=LLM)


@pytest.fixture
def translator(mock_llm):
    return Translator(model_name="gpt-4o", llm=mock_llm)


@pytest.fixture
def mock_input_source():
    return MagicMock(spec=FileInputSource)


@pytest.fixture
def mock_output_source():
    return MagicMock(spec=FileOutputSource)


def test_translate_dryrun(
    translator: Translator, mock_llm, mock_input_source, mock_output_source
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        target_language="fr",
        dryrun=True,
    )

    mock_llm.completion.assert_not_called()
    mock_input_source.read.assert_not_called()
    mock_output_source.write.assert_not_called()


def test_translate_new_file(
    translator: Translator,
    mock_llm,
    mock_input_source,
    mock_output_source,
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = False
    mock_input_source.read.return_value = "Hello, world!"
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        target_language="fr",
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
    mock_output_source.write.assert_called_once_with("Bonjour, le monde!")


def test_translate_with_source(
    translator: Translator, mock_llm, mock_input_source, mock_output_source
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = False
    mock_input_source.read.return_value = "Hello, world!"
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        source_language="en",
        target_language="fr",
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
                "- File extension: .txt",
            },
            {
                "role": "user",
                "content": "User provided text:\n----------\nHello, world!",
            },
        ],
    )
    mock_output_source.write.assert_called_once_with("Bonjour, le monde!")


def test_translate_no_overwrite(
    translator: Translator, mock_llm, mock_input_source, mock_output_source
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = True

    with patch("rich.prompt.Confirm.ask", return_value=False):
        translator.translate(
            input_source=mock_input_source,
            output_source=mock_output_source,
            target_language="fr",
            overwrite=False,
        )

    mock_llm.completion.assert_not_called()
    mock_input_source.read.assert_not_called()
    mock_output_source.write.assert_not_called()


def test_translate_overwrite(
    translator: Translator, mock_llm, mock_input_source, mock_output_source
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = True
    mock_input_source.read.return_value = "Hello, world!"
    mock_output_source.read.return_value = "Bonjour, le monde(existing file)"
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        target_language="fr",
        overwrite=True,
    )

    mock_input_source.read.assert_called_once_with()
    mock_output_source.read.assert_called_once_with()
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
    mock_output_source.write.assert_called_once_with("Bonjour, le monde!")


def test_auto_generate_output_path(
    translator: Translator, mock_llm, mock_input_source, mock_output_source
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = False
    mock_input_source.read.return_value = "Hello, world!"
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        source_language="en",
        target_language="fr",
        overwrite=False,
    )

    mock_output_source.write.assert_called_once_with("Bonjour, le monde!")


def test_auto_generate_fallback(
    translator: Translator, mock_llm, mock_input_source, mock_output_source
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = False
    mock_input_source.read.return_value = "Hello, world!"
    mock_llm.completion.return_value = "Bonjour, le monde!"

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        source_language="en",
        target_language="fr",
        overwrite=False,
    )

    mock_output_source.write.assert_called_once_with("Bonjour, le monde!")


def test_translate_with_request(
    translator: Translator, mock_llm, mock_input_source, mock_output_source
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = False
    mock_input_source.read.return_value = "Hello, world!"
    mock_llm.completion.return_value = "Bonjour, world!"

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        target_language="fr",
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
    mock_output_source.write.assert_called_once_with("Bonjour, world!")


def test_rewrite(
    translator: Translator, mock_llm, mock_input_source, mock_output_source
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = True
    mock_input_source.read.return_value = "Hello, world!"
    mock_output_source.read.return_value = "Hi, world!"
    mock_llm.completion.return_value = "HELLO, WORLD!"

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        overwrite=True,
    )

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
                "Hi, world!",
            },
            {
                "role": "user",
                "content": "User provided text:\n----------\nHello, world!",
            },
        ],
    )
    mock_output_source.write.assert_called_once_with("HELLO, WORLD!")
