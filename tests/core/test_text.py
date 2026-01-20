from ankitools.core.text import find_intersection, highlight_sentence

def test_find_intersection_simple():
    assert find_intersection("改修", "大規模な改修が行われる") == "改修"

def test_find_intersection_conjugated():
    assert find_intersection("話し込む", "友人と話し込んだ") == "話し込"

def test_find_intersection_no_match():
    assert find_intersection("りんご", "みかんはおいしい") is None

def test_find_intersection_kanji_stem():
    # "行く" (iku) vs "行きます" (ikimasu) -> "行" (iku)
    assert find_intersection("行く", "行きます") == "行"

def test_highlight_sentence_simple():
    res = highlight_sentence("改修", "大規模な改修が行われる")
    assert res == "大規模な<u><b>改修</b></u>が行われる"

def test_highlight_sentence_conjugated():
    res = highlight_sentence("話し込む", "友人と話し込んだ")
    assert res == "友人と<u><b>話し込</b></u>んだ"

def test_highlight_sentence_no_match():
    res = highlight_sentence("りんご", "みかんはおいしい")
    assert res == "みかんはおいしい"

def test_highlight_sentence_ambiguous():
    # "行く" (len 2) vs "行" (len 1). "行く" should be preferred as it is longer.
    # Sentence: "銀行に行く" (Ginkou ni iku)
    # If we picked "行" from "銀行", result would be "銀<u><b>行</b></u>に行く".
    # If we pick "行く", result is "銀行に<u><b>行く</b></u>".
    res = highlight_sentence("行く", "銀行に行く")
    assert res == "銀行に<u><b>行く</b></u>"
