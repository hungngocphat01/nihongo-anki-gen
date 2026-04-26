import os
from unittest.mock import MagicMock, patch

import pytest

from ankitools.llm.handler import LLMHandler
from ankitools.llm.schema import ModelOutput


def test_default_model_uses_langchain_agent() -> None:
    structured_response = ModelOutput(output=[])
    fake_agent = MagicMock()
    fake_agent.invoke.return_value = {"structured_response": structured_response}

    with patch(
        "ankitools.llm.handler.create_agent", return_value=fake_agent
    ) as mock_create_agent:
        handler = LLMHandler(system_prompt="system prompt")
        result = handler("hello")

    mock_create_agent.assert_called_once_with(
        "google_genai:gemini-2.5-flash",
        system_prompt="system prompt",
        response_format=ModelOutput,
    )
    assert result == structured_response
    fake_agent.invoke.assert_called_once_with(
        {"messages": [{"role": "user", "content": "hello"}]}
    )


def test_openrouter_model_uses_chat_openrouter() -> None:
    structured_response = ModelOutput(output=[])
    fake_structured_model = MagicMock()
    fake_structured_model.invoke.return_value = structured_response
    fake_chat_model = MagicMock()
    fake_chat_model.with_structured_output.return_value = fake_structured_model

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
        with patch(
            "ankitools.llm.handler.ChatOpenRouter", return_value=fake_chat_model
        ) as mock_chat_openrouter:
            handler = LLMHandler(
                model_name="openrouter:deepseek/deepseek-v3.2",
                system_prompt="system prompt",
            )
            result = handler("hello")

    mock_chat_openrouter.assert_called_once_with(
        model="deepseek/deepseek-v3.2",
        temperature=0,
        max_retries=2,
    )
    fake_chat_model.with_structured_output.assert_called_once_with(
        ModelOutput,
        method="json_schema",
    )
    fake_structured_model.invoke.assert_called_once_with(
        [
            ("system", "system prompt"),
            ("human", "hello"),
        ]
    )
    assert result == structured_response


def test_openrouter_import_error_includes_install_hint() -> None:
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
        with patch("ankitools.llm.handler.ChatOpenRouter", None):
            with pytest.raises(ImportError, match="langchain-openrouter"):
                LLMHandler(model_name="openrouter:google/gemini-2.5-flash")


def test_openrouter_default_system_prompt_path_still_works() -> None:
    structured_response = ModelOutput(output=[])
    fake_structured_model = MagicMock()
    fake_structured_model.invoke.return_value = structured_response
    fake_chat_model = MagicMock()
    fake_chat_model.with_structured_output.return_value = fake_structured_model

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
        with patch(
            "ankitools.llm.handler.ChatOpenRouter", return_value=fake_chat_model
        ):
            handler = LLMHandler(model_name="openrouter:google/gemini-2.5-flash")
            result = handler("hello")

    fake_structured_model.invoke.assert_called_once_with([("human", "hello")])
    assert result == structured_response


def test_openrouter_requires_api_key() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
            LLMHandler(model_name="openrouter:google/gemini-2.5-flash")
