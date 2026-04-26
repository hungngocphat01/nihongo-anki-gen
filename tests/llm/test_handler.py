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


def test_openrouter_model_uses_langchain_agent() -> None:
    structured_response = ModelOutput(output=[])
    fake_agent = MagicMock()
    fake_agent.invoke.return_value = {"structured_response": structured_response}

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
        with patch(
            "ankitools.llm.handler.create_agent", return_value=fake_agent
        ) as mock_create_agent:
            handler = LLMHandler(
                model_name="openrouter:google/gemini-2.5-flash",
                system_prompt="system prompt",
            )
            result = handler("hello")

    mock_create_agent.assert_called_once_with(
        "openrouter:google/gemini-2.5-flash",
        system_prompt="system prompt",
        response_format=ModelOutput,
    )
    fake_agent.invoke.assert_called_once_with(
        {"messages": [{"role": "user", "content": "hello"}]}
    )
    assert result == structured_response


def test_openrouter_import_error_includes_install_hint() -> None:
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
        with patch(
            "ankitools.llm.handler.create_agent",
            side_effect=ImportError(
                "Initializing ChatOpenRouter requires the "
                "langchain-openrouter package."
            ),
        ):
            with pytest.raises(ImportError, match="langchain-openrouter"):
                LLMHandler(model_name="openrouter:google/gemini-2.5-flash")


def test_response_format_is_model_output_for_openrouter() -> None:
    fake_agent = MagicMock()

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
        with patch(
            "ankitools.llm.handler.create_agent", return_value=fake_agent
        ) as mock_create_agent:
            LLMHandler(model_name="openrouter:google/gemini-2.5-flash")

    assert mock_create_agent.call_args.kwargs["response_format"] is ModelOutput


def test_openrouter_default_system_prompt_path_still_works() -> None:
    structured_response = ModelOutput(output=[])
    fake_agent = MagicMock()
    fake_agent.invoke.return_value = {"structured_response": structured_response}

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=False):
        with patch("ankitools.llm.handler.create_agent", return_value=fake_agent):
            handler = LLMHandler(model_name="openrouter:google/gemini-2.5-flash")
            result = handler("hello")

    fake_agent.invoke.assert_called_once_with(
        {"messages": [{"role": "user", "content": "hello"}]}
    )
    assert result == structured_response


def test_openrouter_requires_api_key() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
            LLMHandler(model_name="openrouter:google/gemini-2.5-flash")
