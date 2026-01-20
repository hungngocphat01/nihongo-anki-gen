import os
import sys
import yaml
from pathlib import Path

DEFAULT_CONFIG_NAME = 'config.yaml'
DEFAULT_UNIX_CONFIG = os.path.expanduser('~/.config/ankitools/' + DEFAULT_CONFIG_NAME)
DEFAULT_WINDOWS_CONFIG = os.path.join(os.environ.get('APPDATA', '~'), 'ankitools', DEFAULT_CONFIG_NAME)

def get_default_config_path():
    if sys.platform == 'win32':
        return DEFAULT_WINDOWS_CONFIG
    return DEFAULT_UNIX_CONFIG

class BaseConfig:
    def __init__(self, path=None):
        self.path = path or get_default_config_path()
        if not os.path.exists(self.path):
            # If path was explicitly provided but doesn't exist, that's an error.
            # If it's the default path, we just load empty config or let subclasses handle it.
             if path:
                raise FileNotFoundError(f"Config file not found: {path}")
             self.data = {}
        else:
             with open(self.path, encoding='utf-8') as f:
                self.data = yaml.safe_load(f) or {}

    def get_section(self, section_name):
        return self.data.get(section_name, {})
