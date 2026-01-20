from difflib import SequenceMatcher
from typing import Optional, Union
from difflib import Match

def _contains_kanji(text: str) -> bool:
    """Check if the text contains any Kanji characters."""
    for char in text:
        # Basic CJK Unified Ideographs block
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def _find_intersection_match(word: str, sentence: str) -> Optional[Match]:
    """
    Finds the longest common substring match object.
    Internal helper returning difflib.Match.
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
    if match.size < 2 and len(word) > 1:
        if not _contains_kanji(matched_str):
            return None
            
    return match

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
    match = _find_intersection_match(word, sentence)
    if not match:
        return None
    return word[match.a : match.a + match.size]

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
    match = _find_intersection_match(word, sentence)
    if not match:
        return sentence
        
    # Use indices for robust replacement (b=start in sequence b (sentence))
    start = match.b
    end = match.b + match.size
    
    original_segment = sentence[start:end]
    return f"{sentence[:start]}<u><b>{original_segment}</b></u>{sentence[end:]}"
