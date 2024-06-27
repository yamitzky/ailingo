from typing import Iterator, cast

import litellm
from litellm.types.utils import ModelResponse


class LLM:
    model_name: str

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def _completion(self, model: str, prompt: str | list[dict]):
        if isinstance(prompt, str):
            messages = [{"content": prompt, "role": "user"}]
        else:
            messages = prompt
        response = litellm.completion(model=model, messages=messages, stream=True)
        return (cast(ModelResponse, chunk) for chunk in response)

    def completion(self, prompt: str | list[dict]) -> str:
        chunks = self._completion(self.model_name, prompt)
        response = litellm.stream_chunk_builder(list(chunks))
        return response.choices[0].message.content  # type: ignore

    def iter_completion(self, prompt: str | list[dict]) -> Iterator[str]:
        chunks = self._completion(self.model_name, prompt)
        for chunk in chunks:
            yield chunk.choices[0].delta.content  # type: ignore
