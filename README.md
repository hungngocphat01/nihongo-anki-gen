# Anki Generator for Japanese from Random Notes

## The goal

**Automating the creation of Japanese Anki flashcards from raw notes.**

My typical workflow involves watching Japanese content and noting down new words (and sometimes their context) into a simple text file. Previously, I had to look up each word individually, search for example sentences on Weblio, or prompt an LLM to generate them one by one.

As I advanced towards N2, the volume of new vocabulary exploded, and manual card creation became a burden. I needed automation.

My raw notes are quite unstructured and random. Sometimes it's just a word, sometimes a phrase, sometimes with a quick meaning in English or Vietnamese:

```text
別人に成りすます
束縛が強め (bạn gái) kiểm soát nhiều
巻き上げる　rip off money from s.o.
スポットを当てる to bring attention
エラ削り gọt cằm
脂肪吸引
糸リフト
切開リフト
```

As you can see, the input is inconsistent. It might be a standalone word, or it might include context-dependent meanings I noted down.

I typically separate my Anki cards into **Single Words** and **Collocations**, using two different decks. This tool handles that separation automatically. You can configure the specific deck names and Note Types in `config.yaml`, as well as map the generated data fields to your specific Anki template structure for each category.

### What this project does

```
+----------------+       +-----------+       +----------------------+
| vocab_list.txt |  -->  |  AnkiGen  |  -->  |  Anki (AnkiConnect)  |
+----------------+       +-----------+       +----------------------+
                               ^
                               |
                               v
                         +-----------+
                         |   Gemini  |
                         +-----------+
```

Very simple:
- Get your random vocabulary notes
- Prompt Gemini to generate the necessary fields for the Anki template **in your desired language**
- Insert into Anki directly (requires AnkiConnect). You can also export it as a JSON file without Anki.

The list of available fields can be found under [Mapping syntax](#mapping-syntax). The prompt is customizable through CLI arguments. The original prompt is in [ankigen/prompt.py](ankigen/prompt.py).

## How to use

1. **Prepare the configuration:**
   See the "Config" section below for details on how to set up your `config.yaml`.

2. **Install the package:**
   ```bash
   cd /path/to/cloned/ankigen
   pip install .
   ```

3. **Get a Gemini API key:**
   Obtain an API key from Gemini (not the GCP API key) and export it in your terminal:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

4. **Run the CLI:**

   **To insert directly into Anki:**
   (Note: You must have [Anki Connect](https://ankiweb.net/shared/info/2055492159) installed and running on your open Anki instance)
   ```bash
   python -m ankigen --input vocab.txt --config config.yaml
   ```

   **To generate a JSON file instead:**
   (Useful if you want to inspect the output before importing)
   ```bash
   python -m ankigen --input vocab.txt --config config.yaml -o output.json
   ```

   **Other options:**
   - `--lang <language>`: Set the target language for meanings and translations (e.g., `english`, `vietnamese`). Default is `vietnamese`.
   - `--jlpt <level>`: Adjust the target difficulty of the generated Japanese example sentences (e.g. `n2`, `n1`).

5. **Sample output:** see [sample_output.json](sample_output.json) (in Vietnamese).

## Config

You must provide a `config.yaml` file to tell the tool how to map the generated data to your specific Anki headers.

### Location

You can provide the path to the config file using the `--config` argument. If not provided, the tool will look for a `config.yaml` file in the default directory:
- Windows: `C:\Users\<YourUsername>\AppData\Roaming\ankigen\config.yaml`
- Linux/Mac: `~/.config/ankigen/config.yaml`

### Required keys
Every key shown in the example below is required. The tool needs to distinguish between "vocab" cards and "collocation" cards, and know which Note Type to use for each. Remember to create the decks in advance before running the tool.

```yaml
decks:
  vocab: N2::Vocab             # Deck name for single words
  collocation: N2::Collocation # Deck name for collocations
templates:
  vocab: 'Your Note Type Name'          # Note Type for single words
  collocation: 'Your Note Type Name'    # Note Type for collocations
mappings:
  vocab:
    # format: <Anki Field Name>: <Generated Key>
    Expression: vocab
    Reading: furigana
    Meaning: meaning
    Example: example
    Translation: example_trans
    HanViet: hanviet
  collocation:
    Expression: vocab
    Reading: furigana
    Meaning: meaning
    Example: example
    Translation: example_trans
    HanViet: hanviet
```

A sample `config.yaml` file is also provided in this repository.

### Mapping syntax
The `mappings` section defines how the LLM output maps to your Anki card fields.
- **Key (Left side):** The exact name of the **Field** in your Anki Note Type.
- **Value (Right side):** The data key generated by this tool.

**The available keys are:**
- `vocab`: The word or phrase itself (exactly as it appeared in your list).
- `furigana`: The reading of the word (hiragana).
- `example`: An example sentence in Japanese.
- `example_trans`: Translation of the example sentence in the desired language.
- `meaning`: The meaning of the word in the desired language.
- `hanviet`: Han-Viet reading (Vietnamese transcription of the kanji).
  > **Note:** The `hanviet` key is only populated when the tool is run with `--language=vietnamese`.

# Acknowledgements

This project is vibecoded with Cursor. The Gemini prompt is written manually.