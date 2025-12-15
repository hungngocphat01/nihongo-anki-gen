import requests
from ankigen.config import AnkiConfig
from ankigen.utils import logger

ANKI_CONNECT_URL = "http://localhost:8765"


class AnkiConnectClient:
    def __init__(self, url=ANKI_CONNECT_URL):
        self.url = url

    def req(self, action, **params):
        r = requests.post(
            self.url, json={"action": action, "version": 6, "params": params}
        )
        r.raise_for_status()
        res = r.json()
        if "error" in res and res["error"]:
            raise Exception(f"Anki-Connect error: {res['error']}")
        return res.get("result")

    def deck_is_ready(self, deck_name):
        decks = self.req("deckNames")
        return deck_name in decks

    def model_is_ready(self, model_name):
        models = self.req("modelNames")
        return model_name in models

    def assert_deck_exists(self, deck_name: str):
        assert self.deck_is_ready(
            deck_name
        ), f"Deck does not exist in Anki: {deck_name}"

    def assert_model_exists(self, model_name: str):
        assert self.model_is_ready(
            model_name
        ), f"Model (card template) does not exist in Anki: {model_name}"

    def validate_mapping(self, model_name: str, keys: list[str]):
        model_keys = self.req("modelFieldNames", modelName=model_name)
        error_keys = [key for key in keys if key not in model_keys]

        if len(error_keys) > 0:
            raise ValueError(
                f"Keys {error_keys} does not exist in card template '{model_name}'. Please check your mapping in `config.yaml`"
            )

    def add_note(self, deck, model_name, fields, tags=None):
        return self.req(
            "addNote",
            note={
                "deckName": deck,
                "modelName": model_name,
                "fields": fields,
                "tags": tags or [],
            },
        )

    def get_api_version(self):
        return self.req("version")

    def validate_config(self, config: AnkiConfig):
        for entry_kind in ["vocab", "collocation"]:
            self.assert_deck_exists(config.decks[entry_kind])
            self.assert_model_exists(config.templates[entry_kind])
            self.validate_mapping(
                config.templates[entry_kind], config.mappings[entry_kind]
            )


def entry_to_anki_fields(entry, mapping):
    return {
        anki_col: getattr(entry, entry_field)
        for anki_col, entry_field in mapping.items()
        if hasattr(entry, entry_field)
    }
