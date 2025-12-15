import os
import sys
from pathlib import Path
import yaml

DEFAULT_CONFIG_NAME = 'config.yaml'
DEFAULT_UNIX_CONFIG = os.path.expanduser('~/.config/ankigen/' + DEFAULT_CONFIG_NAME)
DEFAULT_WINDOWS_CONFIG = os.path.join(os.environ.get('APPDATA', '~'), 'ankigen', DEFAULT_CONFIG_NAME)

SAMPLE_CONFIG = {
    'decks': {
        'vocab': 'Japanese::Vocabulary',
        'collocation': 'Japanese::Collocations',
    },
    'templates': {
        'vocab': 'Basic',
        'collocation': 'Basic'  
    },
    'mappings': {
        'vocab': {
            'index': 'vocab',
            'vocab': 'vocab',
            'kana': 'furigana',
            'example': 'example',
            'translation': 'example_trans',
            'meaning': 'meaning'
        },
        'collocation': {
            'index': 'vocab',
            'vocab': 'vocab',
            'kana': 'furigana',
            'example': 'example',
            'translation': 'example_trans',
            'meaning': 'meaning'
        },
    }
}

def get_default_config_path():
    if sys.platform == 'win32':
        return DEFAULT_WINDOWS_CONFIG
    return DEFAULT_UNIX_CONFIG

def ensure_config_exists(path=None):
    config_path = path or get_default_config_path()
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_path):
        os.makedirs(config_dir, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(SAMPLE_CONFIG, f, sort_keys=False, allow_unicode=True)
    return config_path

class AnkiConfig:
    def __init__(self, path=None):
        self.path = ensure_config_exists(path)
        with open(self.path, encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
        self.decks = self.data.get('decks', {})
        self.mappings = self.data.get('mappings', {})
        self.templates = self.data.get('templates', {})
