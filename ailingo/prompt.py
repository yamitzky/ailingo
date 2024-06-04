from pathlib import Path

import jinja2


class PromptBuilder:
    def __init__(self):
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath=Path(__file__).parent / "prompts")
        )

    def build(
        self,
        input_path: str,
        input_text: str,
        source_language: str | None = None,
        target_language: str | None = None,
        request: str | None = None,
        current_text: str | None = None,
    ) -> list[dict[str, str]]:
        """
        Build prompt for translation or rewrite.
        """

        template_name = "translate.j2" if target_language else "rewrite.j2"
        template = self.jinja_env.get_template(template_name)
        system_prompt = template.render(
            input_path=Path(input_path),
            source_language=source_language,
            target_language=target_language,
            request=request,
            current_text=current_text,
        )

        template = self.jinja_env.get_template("user.j2")
        user_prompt = template.render(
            input_text=input_text,
        )
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
