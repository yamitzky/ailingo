import logging
from logging import getLogger
import os
import subprocess
import tempfile

import typer
from ailingo.translator import DEFAULT_OUTPUT_PATTERN, Translator
from ailingo.utils import setup_logger
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from requests_html import HTMLSession

app = typer.Typer()

err_console = Console(stderr=True)
logger = getLogger(__name__)


@app.command()
def translate(
    file_paths: list[str] = typer.Argument(
        default=None, help="Input file(s) to translate."
    ),
    url: str = typer.Option(None, "-u", "--url", help="URL to translate."),
    source_language: str = typer.Option(
        None, "-s", "--source", help="Source language(Optional)"
    ),
    target_languages_str: str = typer.Option(
        None,
        "-t",
        "--target",
        help="Comma-separated list of target languages. If omitted, original file will be rewritten.",
    ),
    model_name: str = typer.Option(
        "gpt-4o",
        "-m",
        "--model",
        envvar="MODEL_NAME",
        help="Generative AI model to use for translation(e.g. gpt-4o, gemini-1.5-pro).",
    ),
    output_pattern: str = typer.Option(
        None,
        "-o",
        "--output",
        help="Output file name pattern.",
        show_default=DEFAULT_OUTPUT_PATTERN,
    ),
    overwrite: bool = typer.Option(
        False, "-y", "--yes", help="Skip confirmation before overwriting."
    ),
    request: str = typer.Option(
        None,
        "-r",
        "--request",
        help="Add a translation request",
    ),
    edit: bool = typer.Option(False, "-e", "--edit", help="Edit mode."),
    dryrun: bool = typer.Option(
        False, "--dry-run", help="Perform a trial run with no changes made."
    ),
    quiet: bool = typer.Option(
        False, "-q", "--quiet", help="Suppress all output messages."
    ),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode."),
) -> None:
    """
    Translates the specified files.
    """
    setup_logger(logging.DEBUG if debug else None)
    if debug:
        logger.debug("Debug mode enabled.")
    if dryrun:
        logger.debug("Dry run enabled.")

    if target_languages_str:
        target_languages = target_languages_str.split(",")
    else:
        target_languages = []
    if not file_paths:
        file_paths = []
    no_temp_file = bool(dryrun or output_pattern)

    translator = Translator(model_name=model_name)

    # validate arguments
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

    # edit mode
    if edit:
        logger.debug("Edit mode enabled.")
        with (
            tempfile.NamedTemporaryFile(mode="w+", suffix=".txt") as input,
            tempfile.NamedTemporaryFile(
                mode="w+", suffix=".txt", delete=no_temp_file
            ) as output,
        ):
            if not dryrun:
                _run_editor(input.name)
            translator.translate(
                file_path=input.name,
                source_language=source_language,
                target_language=target_languages[0] if target_languages else None,
                output_pattern=output_pattern if output_pattern else output.name,
                overwrite=overwrite if output_pattern else True,
                dryrun=dryrun,
                request=request,
                quiet=quiet,
            )
            output.seek(0)
            print(output.read())
        return

    if url:
        logger.debug("URL mode enabled.")
        with (
            tempfile.NamedTemporaryFile(mode="w+", suffix=".html") as input,
            tempfile.NamedTemporaryFile(
                mode="w+", suffix=".md", delete=no_temp_file
            ) as output,
        ):
            if dryrun:
                text = ""
            else:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    if not quiet:
                        progress.add_task(
                            description=(
                                f":writing_hand: [bold blue]Downloading...[/bold blue] "
                                f"[bright_black]{url}[/bright_black]"
                            ),
                            total=None,
                        )
                    session = HTMLSession()
                    response = session.get(url)
                response.raise_for_status()
                text = response.html.text  # type: ignore
            input.write(text)
            translator.translate(
                file_path=input.name,
                source_language=source_language,
                target_language=target_languages[0] if target_languages else None,
                output_pattern=output_pattern if output_pattern else output.name,
                overwrite=overwrite if output_pattern else True,
                dryrun=dryrun,
                request=request
                or "Original text is extracted from a website. Convert it to markdown.",
                quiet=quiet,
            )
            output.seek(0)
            print(Markdown(output.read()))
        return

    # rewrite mode
    if not target_languages:
        logger.debug("Rewrite mode enabled.")
        for file_path in file_paths:
            translator.translate(
                file_path=file_path,
                source_language=source_language,
                target_language=None,
                output_pattern=output_pattern,
                overwrite=overwrite,
                dryrun=dryrun,
                request=request,
                quiet=quiet,
            )
        return

    # normal mode
    logger.debug("Normal mode enabled.")
    for file_path in file_paths:
        for target_language in target_languages:
            translator.translate(
                file_path=file_path,
                source_language=source_language,
                target_language=target_language,
                output_pattern=output_pattern,
                overwrite=overwrite,
                dryrun=dryrun,
                request=request,
                quiet=quiet,
            )


def _run_editor(file_path: str):
    editor = os.getenv("EDITOR", "vi")
    try:
        subprocess.run([editor, file_path], check=True)
    except FileNotFoundError:
        err_console.print(f"Editor '{editor}' not found. Please set a default editor.")
        raise typer.Exit(code=1)

    if os.path.getsize(file_path) == 0:
        err_console.print("No changes made. Exiting...")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
