# ankitools

CLI productivity tools for Anki.

## Features

- **gencards**: Automate the creation of Anki flashcards from raw vocabulary lists using LLMs (Gemini).
- **cloze-transform**: Highlight vocabulary in example sentences within existing Anki cards (e.g. `word` -> `...<u><b>word</b></u>...`).

## Installation

```bash
cd /path/to/ankitools
pip install .
```

## Configuration

The tool expects a configuration file at `~/.config/ankitools/config.yaml` (Linux/Mac) or `%APPDATA%\ankitools\config.yaml` (Windows).
You can also specify a config file with the `--config` argument.

See `config.yaml.example` for the required structure.

```yaml
gencards:
  decks:
    vocab: Japanese::Vocabulary
    collocation: Japanese::Collocations
  templates:
    vocab: 'Nihongo Sentence Translation'
    collocation: 'Nihongo Sentence Translation'
  mappings:
    vocab:
      Expression: vocab
      Reading: furigana
      # ...

cloze_transform:
  default_deck: "Japanese::Vocabulary"
  fields:
    word: "Expression"
    sentence: "Example"
```

## Usage

### gencards

Generate flashcards from a text file containing vocabulary.

```bash
# Generate and insert directly into Anki (requires AnkiConnect)
ankitools gencards vocab_list.txt

# Generate to JSON file (no Anki required)
ankitools gencards vocab_list.txt --output output.json

# Specify config file
ankitools gencards vocab_list.txt --config my_config.yaml
```

**Options:**
- `--anki-connect <url>`: AnkiConnect URL (default: http://localhost:8765)
- `--llm <model>`: LLM model (default: google_genai:gemini-2.5-flash)
- `--lang <language>`: Target language (default: vietnamese)
- `--jlpt <level>`: JLPT level (default: n3)

### cloze-transform

Scan existing cards and highlight the target word in the example sentence (does not use LLM).

```bash
# Dry run (preview changes without applying) - uses default deck from config
ankitools cloze-transform

# Apply changes to Anki
ankitools cloze-transform --write

# Specify deck override
ankitools cloze-transform --deck "My::Other::Deck"

# Limit processing to first N cards (for testing)
ankitools cloze-transform --deck "My::Deck" --limit 10

# Specify config file
ankitools cloze-transform --config my_config.yaml --deck "My::Deck"
```

**Options:**
- `--deck <name>`: Target deck name (overrides `default_deck` in config)
- `--write`: Apply changes (default is dry-run preview mode)
- `--limit <n>`: Limit to first N cards
- `--config <path>`: Config file path (default: `~/.config/ankitools/config.yaml`)

**Features:**
- **Smart Matching**: Detects conjugated forms (e.g., highlights "話し込" in "話し込んだ" for word "話し込む").
- **Safety**: Defaults to Dry Run mode with rich preview.
- **Idempotent**: Skips cards that already have highlighting (`<u><b>...</b></u>`).

## Requirements

- Python 3.8+
- Anki with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) installed
- Google Gemini API Key (`export GOOGLE_API_KEY="..."`)
