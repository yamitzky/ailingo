import os
import subprocess
import tempfile

import typer
from rich import print
from rich.console import Console

from transpa.translator import DEFAULT_OUTPUT_PATTERN, Translator

app = typer.Typer()

err_console = Console(stderr=True)


@app.command()
def translate(
    file_paths: list[str] = typer.Argument(
        default=None, help="Input file(s) to translate."
    ),
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
) -> None:
    """
    Translates the specified files.
    """
    if target_languages_str:
        target_languages = target_languages_str.split(",")
    else:
        target_languages = []

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

    # edit mode
    if edit:
        no_temp_file = bool(dryrun or output_pattern)
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
                overwrite=True,
                dryrun=dryrun,
                request=request,
                quiet=quiet,
            )
            output.seek(0)
            print(output.read())
        return

    # rewrite mode
    if not target_languages:
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
