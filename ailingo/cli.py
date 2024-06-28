import logging
from logging import getLogger
from pathlib import Path
from typing import Annotated, Literal, Optional, cast

import typer
from rich.console import Console

from ailingo.input_source import InputSource
from ailingo.input_source.editor_source import EditorInputSource
from ailingo.input_source.file_source import FileInputSource
from ailingo.input_source.url_source import UrlInputSource
from ailingo.output_source import OutputSource
from ailingo.output_source.console_source import ConsoleOutputSource
from ailingo.output_source.file_source import FileOutputSource
from ailingo.translator import Translator
from ailingo.utils import setup_logger

app = typer.Typer()

err_console = Console(stderr=True)
logger = getLogger(__name__)


InputMode = Literal["edit", "url", "file"]
DEFAULT_OUTPUT_PATTERN = "{parent}/{stem}.{target}{suffix}"


def _comma_separated_list_callback(value: str) -> list[str]:
    if value:
        return value.split(",")
    return []


def _validate(
    edit: bool,
    file_paths: list[Path],
    target_languages: list[str],
    url: str | None,
):
    if edit and file_paths:
        raise typer.BadParameter(
            "File paths cannot be specified in edit mode. Please remove the argument."
        )
    if edit and len(target_languages) > 1:
        raise typer.BadParameter(
            "Multiple target languages cannot be specified in edit mode."
        )
    if edit and url:
        raise typer.BadParameter("Cannot specify both url and edit.")
    if url and len(target_languages) > 1:
        raise typer.BadParameter(
            "Multiple target languages cannot be specified with url."
        )
    if file_paths and url:
        raise typer.BadParameter("Cannot specify both file_paths and url.")
    if not file_paths and not url and not edit:
        raise typer.BadParameter("No input source specified.")


def _get_input_sources(
    input_mode: InputMode,
    file_paths: list[Path],
    url: str | None,
    quiet: bool,
) -> list[InputSource]:
    if input_mode == "edit":
        return [EditorInputSource()]
    elif input_mode == "url":
        return [UrlInputSource(url or "", quiet=quiet)]
    else:
        return [FileInputSource(path) for path in file_paths]


def _get_output_sources(
    input_mode: InputMode,
    input_source: InputSource,
    output_pattern: str | None,
    source_language: str | None,
    target_language: str | None,
) -> OutputSource:
    prefer_markdown = input_mode == "url" or Path(input_source.path).suffix == ".md"
    if output_pattern == "-":
        return ConsoleOutputSource(markdown=prefer_markdown)
    elif output_pattern:
        return FileOutputSource.from_pattern(
            input_source.path,
            output_pattern,
            source=source_language,
            target=target_language,
        )
    elif input_mode == "url" or input_mode == "edit":
        return ConsoleOutputSource(markdown=prefer_markdown)
    elif source_language and target_language:
        # output pattern not specified, but file mode (replace {src} with {target})
        return FileOutputSource.from_replacement(
            input_source.path, source_language, target_language
        )
    elif target_language:
        # output pattern not specified, but file mode (default pattern)
        return FileOutputSource.from_pattern(
            input_source.path, DEFAULT_OUTPUT_PATTERN, target=target_language
        )
    else:
        # otherwise, rewrite original file (rewrite mode)
        return FileOutputSource(input_source.path)


@app.command()
def translate(
    file_paths: Annotated[
        Optional[list[Path]],
        typer.Argument(
            help="Input file(s) to translate.",
            dir_okay=False,
            exists=True,
        ),
    ] = None,
    url: Annotated[
        Optional[str], typer.Option("-u", "--url", help="URL to translate.")
    ] = None,
    source_language: Annotated[
        Optional[str],
        typer.Option("-s", "--source", help="Source language (Optional)"),
    ] = None,
    _target_languages: Annotated[
        list,  # list[str] not work
        typer.Option(
            "-t",
            "--target",
            help="Comma-separated list of target languages. If omitted, original file will be rewritten.",
            parser=_comma_separated_list_callback,
        ),
    ] = [],
    model_name: Annotated[
        str,
        typer.Option(
            "-m",
            "--model",
            envvar="AILINGO_MODEL",
            help="Generative AI model to use for translation (e.g. gpt-4o, gemini-1.5-pro).",
        ),
    ] = "gpt-4o",
    output_pattern: Annotated[
        Optional[str],
        typer.Option(
            "-o",
            "--output",
            help="Output file name pattern.",
            show_default=DEFAULT_OUTPUT_PATTERN,
        ),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option("-y", "--yes", help="Skip confirmation before overwriting"),
    ] = False,
    request: Annotated[
        Optional[str],
        typer.Option(
            "-r",
            "--request",
            help="Add a translation request.",
        ),
    ] = None,
    edit: Annotated[bool, typer.Option("-e", "--edit", help="Edit mode.")] = False,
    dryrun: Annotated[
        bool,
        typer.Option("--dry-run", help="Perform a trial run with no changes made."),
    ] = False,
    quiet: Annotated[
        bool, typer.Option("-q", "--quiet", help="Suppress all output messages.")
    ] = False,
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug mode.")] = False,
    stream: Annotated[
        Optional[bool],
        typer.Option(
            "--stream",
            help="Enable/disable streaming output. Default is not streaming. (Experimental)",
        ),
    ] = False,
) -> None:
    """
    Translates the specified files.
    """
    setup_logger(logging.DEBUG if debug else None)
    if debug:
        logger.debug("Debug mode enabled.")
    if dryrun:
        logger.debug("Dry run enabled.")

    if not file_paths:
        file_paths = []
    target_languages = cast(list[str], _target_languages)

    translator = Translator(model_name=model_name)

    # validate arguments
    _validate(
        edit=edit,
        file_paths=file_paths,
        target_languages=target_languages,
        url=url,
    )

    if edit:
        input_mode = "edit"
    elif url:
        input_mode = "url"
    else:
        input_mode = "file"
    logger.debug(f"{input_mode.capitalize()} mode enabled.")

    input_sources = _get_input_sources(input_mode, file_paths, url, quiet)
    if input_mode == "url" and not request:
        request = "Original text is extracted from a website. Convert it to markdown."

    for input_source in input_sources:
        for target_language in target_languages or [None]:
            output_source = _get_output_sources(
                input_mode,
                input_source,
                output_pattern,
                source_language,
                target_language,
            )
            translator.translate(
                input_source=input_source,
                output_source=output_source,
                source_language=source_language,
                target_language=target_language,
                overwrite=overwrite,
                dryrun=dryrun,
                request=request,
                quiet=quiet,
                stream=stream,
            )


if __name__ == "__main__":
    app()
