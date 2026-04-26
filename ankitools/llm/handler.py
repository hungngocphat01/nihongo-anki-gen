import os
from typing import Optional

from langchain.agents import create_agent

from ankitools.llm.schema import ModelOutput


class LLMHandler:
    def __init__(
        self,
        model_name: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        config=None,
    ):
        self.model = model_name or "google_genai:gemini-2.5-flash"
        self.system_prompt = system_prompt

        if self._is_openrouter_model() and not os.getenv("OPENROUTER_API_KEY"):
            raise ValueError(
                "OPENROUTER_API_KEY is required when using the OpenRouter provider."
            )

        try:
            self.llm = create_agent(
                self.model,
                system_prompt=self.system_prompt,
                response_format=ModelOutput,
            )
        except ImportError as exc:
            if self._is_openrouter_model() and "langchain-openrouter" in str(exc):
                raise ImportError(
                    "OpenRouter support requires the langchain-openrouter package. "
                    "Install project dependencies again after pulling this change."
                ) from exc
            raise

    def _is_openrouter_model(self) -> bool:
        return self.model.startswith("openrouter:")

    def __call__(self, input: str) -> ModelOutput:
        llm_output = self.llm.invoke(
            {"messages": [{"role": "user", "content": input}]}
        )

        return llm_output["structured_response"]
