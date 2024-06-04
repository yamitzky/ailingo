from ailingo.output_source.console_source import ConsoleOutputSource


def test_console_output_source():
    console_source = ConsoleOutputSource()
    assert console_source.path == "(console)"
    assert console_source.readable is False
    assert console_source.markdown is False
    assert console_source.exists() is False


def test_console_output_source_write(capsys):
    console_source = ConsoleOutputSource()
    console_source.write("test")
    captured = capsys.readouterr()
    assert captured.out == "test\n"
