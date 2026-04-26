import sys
from ankitools.core.utils import logger
from ankitools.core.anki import AnkiConnectClient, entry_to_anki_fields, ANKI_CONNECT_URL
from ankitools.llm.handler import LLMHandler
from ankitools.llm.prompt import Prompt
from ankitools.llm.schema import Entry
from ankitools.config.gencards import GencardsConfig


def compose_user_prompt(
    user_prompt_template: str, input: str, target_lang: str, jlpt: str
) -> str:
    return user_prompt_template.format(
        input_list=input, target_lang=target_lang, jlpt=jlpt.upper()
    )


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


def anki_insert(anki: AnkiConnectClient, config: GencardsConfig, entry: Entry):
    assert entry.kind in (
        "vocab",
        "collocation",
    ), f"Invalid entry kind returned by LLM: {entry.kind}"
    
    deck = config.decks.get(entry.kind)
    template = config.templates.get(entry.kind)
    mapping = config.mappings.get(entry.kind)
    
    if not deck or not template or not mapping:
        raise ValueError(f"Missing config for entry kind: {entry.kind}. Check your config file.")

    note = entry_to_anki_fields(entry, mapping)
    anki.add_note(deck, template, note, [])


def setup_parser(parser):
    parser.add_argument("input", help="Input wordlist file")
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
        "--llm",
        help=(
            "LLM to use. Examples: google_genai:gemini-2.5-flash or "
            "openrouter:google/gemini-2.5-flash"
        ),
        default="google_genai:gemini-2.5-flash",
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


def run(args):
    config = GencardsConfig(args.config)
    
    # Simple validation that config loaded something useful
    if not config.decks and not args.output:
         logger.warning("No 'gencards' configuration found in config file. Proceeding but Anki insertion might fail if not using --output.")

    anki = AnkiConnectClient(args.anki_connect)
    if not args.output:
        logger.info(
            f"Successfully connected to AnkiConnect v{anki.get_api_version()}"
        )
        # Validation logic moved here
        for entry_kind in ["vocab", "collocation"]:
            if entry_kind in config.decks:
                anki.assert_deck_exists(config.decks[entry_kind])
            if entry_kind in config.templates:
                anki.assert_model_exists(config.templates[entry_kind])
                if entry_kind in config.mappings:
                    anki.validate_mapping(
                        config.templates[entry_kind], config.mappings[entry_kind]
                    )

    input_text = construct_word_list(args.input)
    logger.info(f"Using config: {config.path}")
    logger.info(f"Processing word list:\n{input_text}")

    prompt = Prompt(args.sys_prompt, args.user_prompt)
    llm = LLMHandler(model_name=args.llm, system_prompt=prompt.system)

    logger.info("Waiting results from LLM")
    model_response = generate(input_text, prompt.user, args.lang, args.jlpt, llm)

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
        except Exception as e:
            stats["fail"] += 1
            stats["fail_words"].append(entry.vocab)
            logger.error(f"Failed to insert {entry.vocab}: {e}")

    if stats["fail"] > 0:
        logger.info(f"❌ {stats['fail']} failed items: {stats['fail_words']}")
        logger.info("If they existed in your specified decks, this is an expected behavior")
