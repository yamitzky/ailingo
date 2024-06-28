from logging import getLogger
from typing import Iterator

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from ailingo.input_source import InputSource
from ailingo.llm import LLM
from ailingo.output_source import OutputSource
from ailingo.prompt import PromptBuilder

logger = getLogger(__name__)


class Translator:
    def __init__(
        self,
        model_name: str,
        llm: LLM | None = None,
        prompt_builder: PromptBuilder | None = None,
    ) -> None:
        self.llm = llm or LLM(model_name)
        self.model_name = model_name
        self.prompt_builder = prompt_builder or PromptBuilder()

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
        stream: bool | None = None,
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

        if stream:
            output_source.write_stream(translated_text)
        else:
            output_source.write("".join(translated_text))

        if not quiet:
            print(
                f":white_check_mark: [bold green]Translated![/bold green] "
                f"[bright_black]{output_source.path}[/bright_black]"
            )

    def _translate_text(
        self,
        input_source: InputSource,
        text: str,
        current_text: str | None,
        source_language: str | None,
        target_language: str | None,
        request: str | None,
    ) -> Iterator[str]:
        """
        Translates the specified text into the specified language using LLM.
        """
        prompt = self.prompt_builder.build(
            input_path=input_source.path,
            input_text=text,
            source_language=source_language,
            target_language=target_language,
            request=request,
            current_text=current_text,
        )
        logger.debug(f"Model: {self.model_name}")
        logger.debug(f"Prompt: {prompt}")
        response = self.llm.iter_completion(prompt)
        return response
