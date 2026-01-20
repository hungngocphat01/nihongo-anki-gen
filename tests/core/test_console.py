import pytest
from ankitools.core.console import print_change_preview

def test_print_change_preview_basic(capsys):
    changes = [
        {
            "word": "apple",
            "old": "I eat an apple.",
            "new": "I eat an <u><b>apple</b></u>."
        }
    ]
    print_change_preview(changes)
    captured = capsys.readouterr()
    
    # Check for table headers
    assert "Word" in captured.out
    assert "Original" in captured.out
    assert "Cloze" in captured.out
    
    # Check for content
    assert "apple" in captured.out
    assert "I eat an apple." in captured.out
    
    # Check that tags are stripped/formatted (raw tags shouldn't appear)
    assert "<u><b>" not in captured.out
    assert "</b></u>" not in captured.out

def test_print_change_preview_empty(capsys):
    print_change_preview([])
    captured = capsys.readouterr()
    # Should probably print something indicating no changes or just an empty table/nothing
    # For now, just ensure no error.
    assert captured.err == ""
