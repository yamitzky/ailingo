from ailingo.input_source import InputSource
from ailingo.prompt import PromptBuilder


class MockInputSource(InputSource):
    def __init__(self, path: str):
        self._path = path

    @property
    def path(self) -> str:
        return self._path

    def read(self) -> str:
        return ""


def test_generate_translate_prompt():
    generator = PromptBuilder()
    input_source = MockInputSource(path="path/to/myfile.py")
    prompt = generator.build(
        input_path=input_source.path,
        input_text="Hello, world!",
        source_language="en",
        target_language="ja",
        request="翻訳のリクエスト",
        current_text="現在のテキスト",
    )
    assert "You are a translator that translates files." in prompt[0]["content"]
    assert "- File extension: .py" in prompt[0]["content"]
    assert "- Source language code: en" in prompt[0]["content"]
    assert "- Target language code: ja" in prompt[0]["content"]
    assert "- Additional request: 翻訳のリクエスト" in prompt[0]["content"]
    assert "Also, some content has been previously translated." in prompt[0]["content"]
    assert "現在のテキスト" in prompt[0]["content"]
    assert "User provided text:" in prompt[1]["content"]
    assert "Hello, world!" in prompt[1]["content"]

    assert prompt[0]["role"] == "system"
    assert prompt[1]["role"] == "user"


def test_generate_rewrite_prompt():
    builder = PromptBuilder()
    input_source = MockInputSource(path="path/to/Dockerfile")
    prompt = builder.build(
        input_path=input_source.path,
        input_text="Hello, world!",
        source_language="ja",
        target_language=None,
        request="リライトのリクエスト",
        current_text="現在のテキスト",
    )
    assert "You are a writer who rewrites text." in prompt[0]["content"]
    assert "- File name: Dockerfile" in prompt[0]["content"]
    assert "- Source language code: ja" in prompt[0]["content"]
    assert "- Target language code:" not in prompt[0]["content"]
    assert "- Additional request: リライトのリクエスト" in prompt[0]["content"]
    assert "Also, some content has been previously translated." in prompt[0]["content"]
    assert "現在のテキスト" in prompt[0]["content"]

    assert "User provided text:" in prompt[1]["content"]
    assert "Hello, world!" in prompt[1]["content"]

    assert prompt[0]["role"] == "system"
    assert prompt[1]["role"] == "user"
