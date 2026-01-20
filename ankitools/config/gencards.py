from ankitools.core.config import BaseConfig

class GencardsConfig(BaseConfig):
    def __init__(self, path=None):
        super().__init__(path)
        section = self.get_section('gencards')
        self.decks = section.get('decks', {})
        self.templates = section.get('templates', {})
        self.mappings = section.get('mappings', {})
