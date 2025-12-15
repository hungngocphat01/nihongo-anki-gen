import argparse
import sys
from typing import Tuple

from ankigen.llm import LLMHandler
from ankigen.config import AnkiConfig
from ankigen.anki import ANKI_CONNECT_URL, AnkiConnectClient, entry_to_anki_fields
from ankigen.prompt import Prompt
from ankigen.schema import Entry
from ankigen.utils import logger


def compose_user_prompt(
    user_prompt_template: str, input: str, target_lang: str, jlpt: str
) -> str:
    return user_prompt_template.format(
        input_list=input, target_lang=target_lang, jlpt=jlpt.upper()
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="ankigen - Anki Flashcard Generator via LLM"
    )
    parser.add_argument("--input", "-i", required=False, help="Input wordlist file")
    parser.add_argument(
        "--output",
        "-o",
        required=False,
        default=None,
        help="Output to JSON instead of AnkiConnect",
    )
    parser.add_argument(
        "--anki-connect", help="URL to AnkiConnect server", default=ANKI_CONNECT_URL
    )
    parser.add_argument(
        "--llm", help="LLM to use", default="google_genai:gemini-2.5-flash"
    )
    parser.add_argument("--sys-prompt", required=False, help="System prompt file (txt)")
    parser.add_argument(
        "--user-prompt", required=False, help="User prompt template (txt)"
    )
    parser.add_argument("--config", required=False, help="YAML config file")
    parser.add_argument(
        "--lang", default="vietnamese", help="Example sentence language"
    )
    parser.add_argument(
        "--jlpt", default="n3", help="Difficulty of the example sentence"
    )
    return parser.parse_args()


def construct_word_list(input_path: str) -> str:
    with open(input_path, "rt", encoding="utf-8") as f:
        lines = [x.strip() for x in f.readlines() if len(x) > 0]
    return "\n".join([f"{idx + 1}. {word}" for idx, word in enumerate(lines)])


def generate(
    input_list: str,
    user_prompt_template: str,
    lang: str,
    jlpt: str,
    llm: LLMHandler,
):
    input_prompt = compose_user_prompt(user_prompt_template, input_list, lang, jlpt)
    llm_output = llm(input_prompt)

    return llm_output


def anki_insert(anki: AnkiConnectClient, config: AnkiConfig, entry: Entry):
    assert entry.kind in (
        "vocab",
        "collocation",
    ), f"Invalid entry kind returned by LLM: {entry.kind}"
    deck, template, mapping = (
        config.decks[entry.kind],
        config.templates[entry.kind],
        config.mappings[entry.kind],
    )
    note = entry_to_anki_fields(entry, mapping)
    anki.add_note(deck, template, note, [])


def main_cli() -> None:
    args = parse_args()
    config = AnkiConfig(args.config)

    if not args.config and not args.input:
        print("--input is required")
        sys.exit(-1)

    anki = AnkiConnectClient(args.anki_connect)
    if not args.output:
        logger.info(
            f"Successfully connected to AnkiConnect v{anki.get_api_version()}"
        )
        anki.validate_config(config)

    input = construct_word_list(args.input)
    logger.info(f"Using config: {args.config}")
    logger.info(f"Processing word list:\n{input}")

    prompt = Prompt(args.sys_prompt, args.user_prompt)
    llm = LLMHandler(model_name=args.llm, system_prompt=prompt.system)

    logger.info("Waiting results from LLM")
    model_response = generate(input, prompt.user, args.lang, args.jlpt, llm)

    if args.output:
        with open(args.output, "wt", encoding="utf-8") as f:
            f.write(model_response.model_dump_json(indent=2))
        logger.info("Wrote results to JSON file")
        return

    logger.info("Writing results to Anki")

    stats = {"fail": 0, "fail_words": []}
    for entry in model_response.output:
        try:
            anki_insert(anki, config, entry)
        except:
            stats["fail"] += 1
            stats["fail_words"].append(entry.vocab)

    if stats["fail"] > 0:
        logger.info(f"❌ {stats['fail']} failed items: {stats['fail_words']}")
        logger.info("If they existed in your specified decks, this is an expected behavior")


if __name__ == "__main__":
    main_cli()
