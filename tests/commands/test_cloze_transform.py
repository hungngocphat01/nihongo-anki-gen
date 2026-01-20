import pytest
from unittest.mock import MagicMock, patch, call
from argparse import Namespace
from pathlib import Path
from ankitools.commands import cloze_transform
from ankitools.config.cloze_transform import ClozeTransformConfig

@pytest.fixture
def mock_client():
    with patch('ankitools.commands.cloze_transform.AnkiConnectClient') as MockClient:
        client = MockClient.return_value
        # Default mock behaviors
        client.deck_is_ready.return_value = True
        client.find_notes.return_value = [1, 2]
        client.notes_info.return_value = [
            {
                "noteId": 1,
                "fields": {
                    "Expr": {"value": "行く"},
                    "Ex": {"value": "銀行に行く"}
                }
            },
            {
                "noteId": 2,
                "fields": {
                    "Expr": {"value": "りんご"},
                    "Ex": {"value": "みかんはおいしい"} # No match
                }
            }
        ]
        yield client

@pytest.fixture
def mock_config():
    with patch('ankitools.commands.cloze_transform.ClozeTransformConfig') as MockConfig:
        config = MockConfig.return_value
        config.default_deck = "TestDeck"
        config.fields.word = "Expr"
        config.fields.sentence = "Ex"
        yield config

def test_run_dry_run(mock_client, mock_config, capsys):
    args = Namespace(
        config=Path("dummy.yaml"),
        deck=None,
        write=False,
        limit=None
    )
    
    cloze_transform.run(args)
    
    # Check findNotes call
    mock_client.find_notes.assert_called_with('"deck:TestDeck"')
    
    # Check notesInfo call
    mock_client.notes_info.assert_called_with([1, 2])
    
    # Check updateNoteFields NOT called
    mock_client.update_note_fields.assert_not_called()
    
    # Check output
    captured = capsys.readouterr()
    # Should show the transformed sentence preview (using rich console, so checking content)
    # The console prints via 'rich', which usually goes to stdout.
    # Note: rich might detect non-tty and behave differently, but we should see content.
    assert "行く" in captured.out
    assert "銀行に行く" in captured.out

def test_run_write_mode(mock_client, mock_config):
    args = Namespace(
        config=Path("dummy.yaml"),
        deck="OverrideDeck",
        write=True,
        limit=None
    )
    
    cloze_transform.run(args)
    
    # Check deck override
    mock_client.find_notes.assert_called_with('"deck:OverrideDeck"')
    
    # Check updateNoteFields called for Note 1 (the match)
    # Note 1 transforms "銀行に行く" -> "銀行に<u><b>行く</b></u>"
    expected_sent = "銀行に<u><b>行く</b></u>"
    mock_client.update_note_fields.assert_called_once_with(1, {"Ex": expected_sent})

def test_run_limit(mock_client, mock_config):
    args = Namespace(
        config=Path("dummy.yaml"),
        deck=None,
        write=False,
        limit=1
    )
    
    mock_client.find_notes.return_value = [1, 2, 3]
    
    cloze_transform.run(args)
    
    # Should only process first note
    mock_client.notes_info.assert_called_with([1])

def test_skip_already_transformed(mock_client, mock_config):
    mock_client.notes_info.return_value = [
        {
            "noteId": 99,
            "fields": {
                "Expr": {"value": "Test"},
                "Ex": {"value": "Already <u><b>Test</b></u> Done"}
            }
        }
    ]
    
    args = Namespace(
        config=Path("dummy.yaml"),
        deck=None,
        write=True,
        limit=None
    )
    
    cloze_transform.run(args)
    
    mock_client.update_note_fields.assert_not_called()
