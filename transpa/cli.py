import typer

from transpa.translator import DEFAULT_OUTPUT_PATTERN, Translator

app = typer.Typer()


@app.command()
def translate(
    file_paths: list[str] = typer.Argument(..., help="Input file(s) to translate."),
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
    for file_path in file_paths:
        if target_languages:
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
        else:
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


if __name__ == "__main__":
    app()
