import os
from typing import Optional

from langchain.agents import create_agent

from ankitools.llm.schema import ModelOutput

try:
    from langchain_openrouter import ChatOpenRouter
except ImportError:
    ChatOpenRouter = None


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

        if self._is_openrouter_model():
            self.llm = self._create_openrouter_llm()
        else:
            self.llm = create_agent(
                self.model,
                system_prompt=self.system_prompt,
                response_format=ModelOutput,
            )

    def _is_openrouter_model(self) -> bool:
        return self.model.startswith("openrouter:")

    def _create_openrouter_llm(self):
        if ChatOpenRouter is None:
            raise ImportError(
                "OpenRouter support requires the langchain-openrouter package. "
                "Install project dependencies again after pulling this change."
            )

        return ChatOpenRouter(
            model=self.model.removeprefix("openrouter:"),
            temperature=0,
            max_retries=2,
        ).with_structured_output(ModelOutput, method="json_schema")

    def __call__(self, input: str) -> ModelOutput:
        if self._is_openrouter_model():
            messages = []
            if self.system_prompt:
                messages.append(("system", self.system_prompt))
            messages.append(("human", input))
            return self.llm.invoke(messages)

        llm_output = self.llm.invoke(
            {"messages": [{"role": "user", "content": input}]}
        )

        return llm_output["structured_response"]
