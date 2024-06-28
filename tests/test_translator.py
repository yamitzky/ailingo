from unittest.mock import MagicMock, patch

import pytest

from ailingo.input_source.file_source import FileInputSource
from ailingo.llm import LLM
from ailingo.output_source.file_source import FileOutputSource
from ailingo.prompt import PromptBuilder
from ailingo.translator import Translator


@pytest.fixture
def mock_llm():
    return MagicMock(spec=LLM)


@pytest.fixture
def mock_prompt():
    return MagicMock(spec=PromptBuilder)


@pytest.fixture
def translator(mock_llm, mock_prompt):
    return Translator(model_name="gpt-4o", llm=mock_llm, prompt_builder=mock_prompt)


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

    mock_llm.iter_completion.assert_not_called()
    mock_input_source.read.assert_not_called()
    mock_output_source.write.assert_not_called()


def test_translate_new_file(
    translator: Translator,
    mock_llm,
    mock_input_source,
    mock_output_source,
    mock_prompt,
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = False
    mock_input_source.read.return_value = "Hello, world!"
    mock_llm.iter_completion.return_value = ["Bonjour, le monde!"]
    mock_prompt.build.return_value = [
        {"role": "system", "content": "You are a translator that translates files."},
        {"role": "user", "content": "User provided text:\n----------\nHello, world!"},
    ]

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        target_language="fr",
        overwrite=False,
    )

    mock_llm.iter_completion.assert_called_once_with(mock_prompt.build.return_value)
    mock_prompt.build.assert_called_once_with(
        input_path="test.txt",
        input_text="Hello, world!",
        source_language=None,
        target_language="fr",
        request=None,
        current_text=None,
    )
    mock_output_source.write.assert_called_once_with("Bonjour, le monde!")


def test_translate_with_source(
    translator: Translator,
    mock_llm,
    mock_input_source,
    mock_output_source,
    mock_prompt,
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = False
    mock_input_source.read.return_value = "Hello, world!"
    mock_llm.iter_completion.return_value = ["Bonjour, le monde!"]
    mock_prompt.build.return_value = [
        {"role": "system", "content": "You are a translator that translates files."},
        {"role": "user", "content": "User provided text:\n----------\nHello, world!"},
    ]

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        source_language="en",
        target_language="fr",
        overwrite=False,
    )

    mock_llm.iter_completion.assert_called_once_with(mock_prompt.build.return_value)
    mock_prompt.build.assert_called_once_with(
        input_path="test.txt",
        input_text="Hello, world!",
        source_language="en",
        target_language="fr",
        request=None,
        current_text=None,
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

    mock_llm.iter_completion.assert_not_called()
    mock_input_source.read.assert_not_called()
    mock_output_source.write.assert_not_called()


def test_translate_overwrite(
    translator: Translator, mock_llm, mock_input_source, mock_output_source, mock_prompt
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = True
    mock_input_source.read.return_value = "Hello, world!"
    mock_output_source.read.return_value = "Bonjour, le monde(existing file)"
    mock_llm.iter_completion.return_value = ["Bonjour, le monde!"]
    mock_prompt.build.return_value = [
        {"role": "system", "content": "You are a translator that translates files."},
        {"role": "user", "content": "User provided text:\n----------\nHello, world!"},
    ]

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        target_language="fr",
        overwrite=True,
    )

    mock_input_source.read.assert_called_once_with()
    mock_output_source.read.assert_called_once_with()
    mock_llm.iter_completion.assert_called_once_with(mock_prompt.build.return_value)
    mock_prompt.build.assert_called_once_with(
        input_path="test.txt",
        input_text="Hello, world!",
        source_language=None,
        target_language="fr",
        request=None,
        current_text="Bonjour, le monde(existing file)",
    )
    mock_output_source.write.assert_called_once_with("Bonjour, le monde!")


def test_translate_with_request(
    translator: Translator, mock_llm, mock_input_source, mock_output_source, mock_prompt
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = False
    mock_input_source.read.return_value = "Hello, world!"
    mock_llm.iter_completion.return_value = ["Bonjour, world!"]
    mock_prompt.build.return_value = [
        {"role": "system", "content": "You are a translator that translates files."},
        {"role": "user", "content": "User provided text:\n----------\nHello, world!"},
    ]

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        target_language="fr",
        overwrite=False,
        request="Do not translate the word 'world'.",
    )

    mock_llm.iter_completion.assert_called_once_with(mock_prompt.build.return_value)
    mock_prompt.build.assert_called_once_with(
        input_path="test.txt",
        input_text="Hello, world!",
        source_language=None,
        target_language="fr",
        request="Do not translate the word 'world'.",
        current_text=None,
    )
    mock_output_source.write.assert_called_once_with("Bonjour, world!")


def test_rewrite(
    translator: Translator, mock_llm, mock_input_source, mock_output_source, mock_prompt
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = True
    mock_input_source.read.return_value = "Hello, world!"
    mock_output_source.read.return_value = "Hi, world!"
    mock_llm.iter_completion.return_value = ["HELLO, WORLD!"]
    mock_prompt.build.return_value = [
        {"role": "system", "content": "You are a writer who rewrites text."},
        {"role": "user", "content": "User provided text:\n----------\nHello, world!"},
    ]

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        overwrite=True,
    )

    mock_llm.iter_completion.assert_called_once_with(mock_prompt.build.return_value)
    mock_prompt.build.assert_called_once_with(
        input_path="test.txt",
        input_text="Hello, world!",
        source_language=None,
        target_language=None,
        request=None,
        current_text="Hi, world!",
    )
    mock_output_source.write.assert_called_once_with("HELLO, WORLD!")


def test_translate_with_streaming(
    translator: Translator,
    mock_llm,
    mock_input_source,
    mock_output_source,
    mock_prompt,
):
    mock_input_source.path = "test.txt"
    mock_output_source.path = "test.fr.txt"
    mock_output_source.exists.return_value = False
    mock_input_source.read.return_value = "Hello, world!"
    mock_llm.iter_completion.return_value = iter(["Bonjour", ", ", "le ", "monde", "!"])
    mock_prompt.build.return_value = [
        {"role": "system", "content": "You are a translator that translates files."},
        {"role": "user", "content": "User provided text:\n----------\nHello, world!"},
    ]

    translator.translate(
        input_source=mock_input_source,
        output_source=mock_output_source,
        target_language="fr",
        overwrite=False,
        stream=True,
    )

    mock_llm.iter_completion.assert_called_once_with(mock_prompt.build.return_value)
    mock_prompt.build.assert_called_once_with(
        input_path="test.txt",
        input_text="Hello, world!",
        source_language=None,
        target_language="fr",
        request=None,
        current_text=None,
    )
    mock_output_source.write_stream.assert_called_once_with(
        mock_llm.iter_completion.return_value
    )
