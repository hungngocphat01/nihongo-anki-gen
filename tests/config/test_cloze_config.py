from ankitools.config.cloze_transform import ClozeTransformConfig
import pytest

def test_load_config():
    data = {
        "cloze_transform": {
            "default_deck": "TestDeck",
            "fields": {"word": "Expr", "sentence": "Ex"}
        }
    }
    cfg = ClozeTransformConfig(data)
    assert cfg.default_deck == "TestDeck"
    assert cfg.fields.word == "Expr"
