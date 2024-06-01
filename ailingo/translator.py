from pathlib import Path
from logging import getLogger

from ailingo.file_manager import FileManager
from ailingo.llm import LLM
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

logger = getLogger(__name__)


DEFAULT_OUTPUT_PATTERN = "{parent}/{stem}.{target}{suffix}"


class Translator:
    def __init__(
        self,
        model_name: str,
        file_manager: FileManager | None = None,
        llm: LLM | None = None,
    ) -> None:
        self.file_manager = file_manager or FileManager()
        self.llm = llm or LLM(model_name)
        self.model_name = model_name

    def translate(
        self,
        file_path: str,
        target_language: str | None = None,
        output_pattern: str | None = None,
        source_language: str | None = None,
        overwrite: bool = False,
        dryrun: bool = False,
        request: str | None = None,
        quiet: bool = False,
    ) -> None:
        """
        Reads the specified file, performs translation, and saves the result.
        """

        output_path = self._generate_output_path(
            file_path=file_path,
            target_language=target_language,
            output_pattern=output_pattern,
            source_language=source_language,
        )

        if dryrun:
            if target_language:
                print(
                    f"[bold blue][DRY RUN][/bold blue] Translating {file_path} to {target_language} "
                    f"and saving to {output_path}."
                )
            else:
                print(
                    f"[bold blue][DRY RUN][/bold blue] Rewriting {file_path} and saving to {output_path}."
                )
            return

        current_content: str | None = None
        if self.file_manager.check_exists(output_path):
            if not overwrite:
                overwrite = Confirm.ask(
                    f"{output_path} already exists. Do you want to overwrite?",
                    default=True,
                )
                if not overwrite:
                    print(f"[yellow]Skipping saving to {output_path}.[/yellow]")
                    return
            current_content = self.file_manager.read_text_file(output_path)

        content = self.file_manager.read_text_file(file_path)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            if not quiet:
                progress.add_task(
                    description=(
                        f":writing_hand: [bold blue]Translating...[/bold blue] "
                        f"[bright_black]{output_path}[/bright_black]"
                    ),
                    total=None,
                )
            translated_text = self._translate_text(
                text=content,
                current_text=current_content,
                file_path=file_path,
                source_language=source_language,
                target_language=target_language,
                request=request,
            )

        self.file_manager.save_text_file(output_path, translated_text)
        if not quiet:
            print(
                f":white_check_mark: [bold green]Translated![/bold green] "
                f"[bright_black]{output_path}[/bright_black]"
            )

    def _generate_output_path(
        self,
        file_path: str,
        target_language: str | None,
        output_pattern: str | None,
        source_language: str | None,
    ) -> str:
        if not output_pattern:
            # if output pattern is not provided and rewriting mode, return the original file path
            if not target_language:
                return file_path

            # if output_pattern is not provided and replacement is possible, use it
            if source_language:
                if output_path := self.file_manager.generate_path_by_replacement(
                    file_path, source_language, target_language
                ):
                    return output_path

        # otherwise, generate the output path using the output pattern
        return self.file_manager.generate_path_by_pattern(
            file_path,
            output_pattern or DEFAULT_OUTPUT_PATTERN,
            target=target_language,
            source=source_language,
        )

    def _translate_text(
        self,
        text: str,
        current_text: str | None,
        file_path: str,
        source_language: str | None,
        target_language: str | None,
        request: str | None,
    ) -> str:
        """
        Translates the specified text into the specified language using LLM.
        """
        suffixes = ".".join(Path(file_path).suffixes)
        file_name = Path(file_path).name
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
        response = self.llm.completion(
            [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
        )
        return response
