from difflib import SequenceMatcher
from typing import Optional

def _contains_kanji(text: str) -> bool:
    """Check if the text contains any Kanji characters."""
    for char in text:
        # Basic CJK Unified Ideographs block
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def find_intersection(word: str, sentence: str) -> Optional[str]:
    """
    Finds the longest common substring between a word and a sentence.
    
    Args:
        word: The target word (e.g., dictionary form).
        sentence: The sentence containing the word (possibly conjugated).
        
    Returns:
        The intersecting substring or None if no significant match found.
        Matches of length 1 are ignored unless:
        - The word itself is length 1
        - OR the match contains a Kanji character
    """
    if not word or not sentence:
        return None
        
    matcher = SequenceMatcher(None, word, sentence)
    match = matcher.find_longest_match(0, len(word), 0, len(sentence))
    
    if match.size == 0:
        return None
        
    matched_str = word[match.a : match.a + match.size]
    
    # Heuristic: Ignore single character matches unless the source word is single character,
    # or the match itself contains Kanji (likely a verb stem).
    # This avoids false positives like matching "ん" or "い" in unrelated words.
    if match.size < 2 and len(word) > 1:
        if not _contains_kanji(matched_str):
            return None
        
    return matched_str

def highlight_sentence(word: str, sentence: str) -> str:
    """
    Highlights the occurrence of the word (or its conjugated form) in the sentence.
    Uses find_intersection to detect the conjugated form.
    
    Args:
        word: The target word.
        sentence: The sentence.
        
    Returns:
        The sentence with the match wrapped in <u><b>...</b></u>.
        If no match is found, returns the original sentence.
    """
    intersection = find_intersection(word, sentence)
    if not intersection:
        return sentence
        
    return sentence.replace(intersection, f"<u><b>{intersection}</b></u>", 1)
