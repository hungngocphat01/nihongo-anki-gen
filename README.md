# ankitools

CLI productivity tools for Anki.

## Features

- **gencards**: Automate the creation of Anki flashcards from raw vocabulary lists using LLMs (Gemini).

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

## Requirements

- Python 3.8+
- Anki with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) installed
- Google Gemini API Key (`export GOOGLE_API_KEY="..."`)
