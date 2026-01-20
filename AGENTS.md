# AGENTS.md

This document provides context, guidelines, and operational procedures for AI agents (and human developers) working on the `ankitools` repository.
It serves as the source of truth for code style, architecture patterns, and build processes.

---

## 1. Project Overview

`ankitools` is a Python-based CLI package designed to enhance productivity for Anki users. 
Its primary current function (`gencards`) is automating flashcard creation from raw vocabulary lists using Large Language Models (LLMs) like Gemini.

- **Package Name**: `ankitools`
- **Build System**: Poetry (`pyproject.toml`)
- **CLI Framework**: `argparse` (Standard Library)
- **Key Libraries**: `langchain`, `pydantic`, `loguru`, `requests`.

---

## 2. Environment & Build

### Dependency Management
The project uses **Poetry** for dependency management.

```bash
# Install dependencies (including dev)
poetry install

# Add a new dependency
poetry add <package_name>

# Add a dev dependency
poetry add --group dev <package_name>
```

### Running the CLI
Always run the CLI through `poetry run` to ensure the virtual environment context is loaded.

```bash
# Display help
poetry run ankitools --help

# Run the 'gencards' command
poetry run ankitools gencards input_list.txt --output cards.json
```

### Testing & Linting
*Note: The project currently lacks a formal test suite. Agents are encouraged to add one.*

**Recommended Tools:**
- **Test Runner**: `pytest`
- **Linter**: `ruff` or `flake8`
- **Formatter**: `black`

**Running Tests (if/when available):**
```bash
# Run all tests
poetry run pytest

# Run a single test file
poetry run pytest tests/test_command.py

# Run a single test function (Useful for agents verifying fixes)
poetry run pytest tests/test_command.py::test_specific_feature -v -s
```

---

## 3. Architecture & Patterns

The codebase follows a modular "Subcommand Pattern".

### Directory Structure
```
ankitools/
├── cli.py                  # Main entry point & router
├── commands/               # Subcommand implementations
│   └── gencards.py         # Example command module
├── config/                 # Configuration schemas
│   └── gencards.py
├── core/                   # Shared utilities
│   ├── anki.py             # AnkiConnect client
│   └── config.py           # Base configuration logic
└── llm/                    # AI/LLM specific logic
```

### Adding a New Command
1.  **Create Module**: Add `ankitools/commands/new_command.py`.
2.  **Implement Setup**: Define `setup_parser(parser)` to register arguments.
3.  **Implement Logic**: Define `run(args)` as the entry point.
4.  **Register**: Import and call `setup_parser` in `ankitools/cli.py`.
5.  **Config**: If it needs config, create `ankitools/config/new_command.py` extending `BaseConfig`.

### Configuration Pattern
- **YAML**: Configuration is stored in `config.yaml` (nested structure).
- **Classes**: specialized config classes (e.g., `GencardsConfig`) wrap the raw YAML data.
- **Usage**:
  ```python
  # In command module
  config = MyCommandConfig(args.config)
  target_deck = config.decks.get('default')
  ```

---

## 4. Code Style Guidelines

### Formatting
- **Style**: Follow **Black** coding style.
- **Line Length**: 88 characters.
- **Indentation**: 4 spaces.
- **Quotes**: Double quotes `"` preferred over single quotes `'` for strings.

### Imports
- **Absolute Imports**: ALWAYS use absolute imports for internal modules.
  - ✅ `from ankitools.core.utils import logger`
  - ❌ `from ..core.utils import logger`
- **Sorting Order**:
  1.  Standard Library (`os`, `sys`, `typing`, `pathlib`)
  2.  Third-Party (`pydantic`, `langchain`, `yaml`)
  3.  Local Project (`ankitools...`)

### Typing
- **Type Hints**: **MANDATORY** for all function signatures and class attributes.
- Use the `typing` module (`List`, `Dict`, `Optional`, `Any`, `Union`).
- Use **Pydantic** models for complex data structures or API schemas.

```python
# ✅ Correct
def fetch_card_data(word: str, limit: int = 10) -> Optional[List[Entry]]:
    ...

# ❌ Incorrect
def fetch_card_data(word, limit=10):
    ...
```

### Naming Conventions
- **Variables/Functions**: `snake_case` (e.g., `generate_cards`, `user_input`)
- **Classes**: `PascalCase` (e.g., `AnkiConnectClient`, `GencardsConfig`)
- **Constants**: `UPPER_CASE` (e.g., `DEFAULT_TIMEOUT`, `ANKI_URL`)
- **Private Members**: `_leading_underscore` (e.g., `_load_yaml`)

### Error Handling
- **Exceptions**: Raise specific exceptions (`ValueError`, `FileNotFoundError`) rather than generic `Exception`.
- **Exit Codes**: If a command fails irrecoverably, use `sys.exit(1)`.
- **Try/Except**: Keep try blocks narrow.

### Logging
- **Library**: Use `loguru` via `ankitools.core.utils.logger`.
- **Levels**:
  - `logger.info()`: Standard user feedback (e.g., "Processing word...").
  - `logger.warning()`: Non-critical issues (e.g., "Config missing, using defaults").
  - `logger.error()`: Operations failures (e.g., "Failed to connect to Anki").
  - `logger.debug()`: Developer details (e.g., "Payload: {...}").
- **No Print**: Avoid `print()` unless the command's primary output is stdout (e.g., JSON export).

---

## 5. Domain Specifics

### Anki Connect
- Interact with Anki ONLY via `ankitools.core.anki.AnkiConnectClient`.
- Always validate that Decks and Models exist using `client.assert_deck_exists()` before attempting inserts.
- Handle connection errors gracefully (Anki might not be running).

### LLM Integration
- All LLM interactions should go through `ankitools.llm.handler.LLMHandler`.
- Do **NOT** hardcode prompts in logic files. Use `ankitools.llm.prompt` or external text files.
- Ensure `GOOGLE_API_KEY` (or relevant env var) is available; fail fast if missing.

### File System
- Use `pathlib.Path` for file path manipulations when possible.
- Ensure file operations specify encoding (usually `encoding='utf-8'`).

---

## 6. Development Checklist for Agents

When tasked with a feature or fix, follow this workflow:

1.  **Analyze**: Understand the requirement and check `config.yaml.example` if config changes are needed.
2.  **Test Plan**: Since tests are sparse, plan how you will verify the change (manual run command or new test file).
3.  **Implement**:
    - Add/Modify code following the **Style Guidelines** above.
    - Ensure Type Hints are present.
    - Add Logging.
4.  **Verify**:
    - Run `poetry run ankitools ...` to verify functionality.
    - Check for linting errors.
5.  **Document**: Update `README.md` or `config.yaml.example` if CLI args or Configs changed.

---

## 7. Common Commands Reference

| Task | Command |
|------|---------|
| Install Deps | `poetry install` |
| Run Tool | `poetry run ankitools [cmd]` |
| Add Dep | `poetry add [package]` |
| Lint (if installed) | `poetry run ruff check .` |
| Format (if installed) | `poetry run black .` |
