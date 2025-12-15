from typing import Optional, List

from langchain.agents import create_agent

from ankigen.utils import logger
from ankigen.schema import Entry, ModelOutput


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
        self.llm = create_agent(
            self.model, system_prompt=self.system_prompt, response_format=ModelOutput
        )

    def __call__(self, input: str) -> ModelOutput:
        llm_output = self.llm.invoke({
            "messages": [
                {"role": "user", "content": input}
            ]
        })
        
        return llm_output["structured_response"]