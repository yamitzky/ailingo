from logging import getLogger
from pathlib import Path

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from ailingo.input_source import InputSource
from ailingo.llm import LLM
from ailingo.output_source import OutputSource

logger = getLogger(__name__)


DEFAULT_OUTPUT_PATTERN = "{parent}/{stem}.{target}{suffix}"


class Translator:
    def __init__(
        self,
        model_name: str,
        llm: LLM | None = None,
    ) -> None:
        self.llm = llm or LLM(model_name)
        self.model_name = model_name

    def translate(
        self,
        input_source: InputSource,
        output_source: OutputSource,
        target_language: str | None = None,
        source_language: str | None = None,
        overwrite: bool = False,
        dryrun: bool = False,
        request: str | None = None,
        quiet: bool = False,
    ) -> None:
        """
        Reads the specified file, performs translation, and saves the result.
        """

        if dryrun:
            if target_language:
                print(
                    f"[bold blue][DRY RUN][/bold blue] Translating {input_source.path} to {target_language} "
                    f"and saving to {output_source.path}."
                )
            else:
                print(
                    f"[bold blue][DRY RUN][/bold blue] Rewriting {input_source.path} and saving to {output_source.path}."
                )
            return

        current_content: str | None = None
        if output_source.exists():
            if not overwrite:
                overwrite = Confirm.ask(
                    f"{output_source.path} already exists. Do you want to overwrite?",
                    default=True,
                )
                if not overwrite:
                    print(f"[yellow]Skipping saving to {output_source.path}.[/yellow]")
                    return
            if output_source.readable:
                current_content = output_source.read()

        content = input_source.read()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            if not quiet:
                progress.add_task(
                    description=(
                        f":writing_hand: [bold blue]Translating...[/bold blue] "
                        f"[bright_black]{output_source.path}[/bright_black]"
                    ),
                    total=None,
                )
            translated_text = self._translate_text(
                input_source=input_source,
                text=content,
                current_text=current_content,
                source_language=source_language,
                target_language=target_language,
                request=request,
            )

        if not quiet:
            print(
                f":white_check_mark: [bold green]Translated![/bold green] "
                f"[bright_black]{output_source.path}[/bright_black]"
            )
        output_source.write(translated_text)

    def _translate_text(
        self,
        input_source: InputSource,
        text: str,
        current_text: str | None,
        source_language: str | None,
        target_language: str | None,
        request: str | None,
    ) -> str:
        """
        Translates the specified text into the specified language using LLM.
        """
        suffixes = ".".join(Path(input_source.path).suffixes)
        file_name = Path(input_source.path).name
        hints: list[str] = []
        if source_language:
            hints.append(f"- Source language code: {source_language}")
        if target_language:
            hints.append(
                f"- Target language code: {target_language}",
            )
        if suffixes:
            hints.append(f"- File extension: {suffixes}")
        else:
            hints.append(f"- File name: {file_name}")
        if request:
            hints.append(f"- Additional request: {request}")
        if current_text:
            hints.append(
                "Also, some content has been previously translated. "
                "Please use the original content as much as possible, and only change and translate the parts "
                f"that differ from the text provided by the user.\n{current_text}"
            )

        if target_language:
            base_prompt = (
                "You are a translator that translates files. "
                "Please translate the content of the file provided by the user.\n"
                "Only output the translation result. Do not output any related comments and code blocks.\n"
                "Please follow the information below for reference.\n"
            )
        else:
            base_prompt = (
                "You are a writer who rewrites text.\n"
                "Please rewrite the provided text to make it more natural without changing the original meaning.\n"
                "As a native speaker, correct any spelling, grammar, or terminology errors.\n"
                "Only output the result. Do not output any related comments and code blocks.\n"
                "Never translate. Don't change the language. Please respect the original language.\n"
                "Please follow the information below for reference.\n"
            )
        prompt = base_prompt + "\n".join(hints)
        logger.debug(f"Model: {self.model_name}")
        logger.debug(f"Prompt: {prompt}")
        logger.debug(f"Text: {text}")
        text = f"User provided text:\n----------\n{text}"
        response = self.llm.completion(
            [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
        )
        return response
