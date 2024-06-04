from dataclasses import dataclass

from requests_html import HTMLSession
from rich.progress import Progress, SpinnerColumn, TextColumn


@dataclass
class UrlInputSource:
    url: str
    quiet: bool = False
    dryrun: bool = False

    @property
    def path(self) -> str:
        return str(self.url)

    def read(self) -> str:
        if self.dryrun:
            return ""

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            if not self.quiet:
                progress.add_task(
                    description=(
                        f":writing_hand: [bold blue]Downloading...[/bold blue] "
                        f"[bright_black]{self.url}[/bright_black]"
                    ),
                    total=None,
                )
            session = HTMLSession()
            response = session.get(self.url)
        response.raise_for_status()
        return response.html.text  # type: ignore
