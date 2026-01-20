import argparse
from typing import List, Dict, Any
from pathlib import Path

from ankitools.core.anki import AnkiConnectClient
from ankitools.config.cloze_transform import ClozeTransformConfig
from ankitools.core.text import highlight_sentence
from ankitools.core.console import print_change_preview
from ankitools.core.utils import logger

def setup_parser(parser: argparse.ArgumentParser):
    parser.add_argument('config', type=Path, nargs='?', default=Path('config.yaml'),
                       help='Path to configuration file')
    parser.add_argument('--deck', type=str, help='Override target deck name')
    parser.add_argument('--write', action='store_true', help='Write changes to Anki (default: Dry Run)')
    parser.add_argument('--limit', type=int, help='Limit number of cards to process')

def run(args: argparse.Namespace):
    # Load config
    try:
        config = ClozeTransformConfig(args.config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    deck_name = args.deck or config.default_deck
    if not deck_name:
        logger.error("No deck specified in config or arguments")
        return

    logger.info(f"Scanning deck: {deck_name}")
    if args.write:
        logger.warning("WRITE MODE ENABLED - Changes will be applied to Anki")
    else:
        logger.info("DRY RUN MODE - No changes will be made")

    client = AnkiConnectClient()
    
    try:
        if not client.deck_is_ready(deck_name):
             logger.error(f"Deck not found: {deck_name}")
             return
    except Exception as e:
        logger.error(f"Failed to connect to Anki: {e}")
        return

    # Query notes
    query = f'"deck:{deck_name}"'
    try:
        note_ids = client.find_notes(query)
    except Exception as e:
        logger.error(f"Failed to query notes: {e}")
        return

    logger.info(f"Found {len(note_ids)} notes")

    if args.limit:
        note_ids = note_ids[:args.limit]
        logger.info(f"Limiting to first {args.limit} notes")

    # Fetch note details
    # AnkiConnect might timeout with too many notes, but let's assume batching isn't needed for now
    # or let the user use --limit. A robust impl would batch.
    notes_info = client.notes_info(note_ids)

    changes = []
    processed_count = 0
    skipped_count = 0
    transformed_count = 0

    word_field = config.fields.word
    sent_field = config.fields.sentence

    for note in notes_info:
        processed_count += 1
        fields = note.get('fields', {})
        nid = note.get('noteId')

        # Check fields exist
        if word_field not in fields or sent_field not in fields or nid is None:
            skipped_count += 1
            continue

        word_val = fields[word_field]['value']
        sent_val = fields[sent_field]['value']

        # Skip empty
        if not word_val or not sent_val:
            skipped_count += 1
            continue

        # Skip already transformed
        if '<u><b>' in sent_val:
            skipped_count += 1
            continue

        # Transform
        new_sent = highlight_sentence(word_val, sent_val)

        if new_sent != sent_val:
            transformed_count += 1
            changes.append({
                "word": word_val,
                "old": sent_val,
                "new": new_sent
            })

            if args.write:
                try:
                    client.update_note_fields(nid, {sent_field: new_sent})
                except Exception as e:
                    logger.error(f"Failed to update note {nid}: {e}")

    # Output results
    if changes:
        print_change_preview(changes)
    else:
        logger.info("No candidates for transformation found.")

    logger.info(f"Summary: Scanned {processed_count}, Skipped {skipped_count}, Transformed {transformed_count}")
