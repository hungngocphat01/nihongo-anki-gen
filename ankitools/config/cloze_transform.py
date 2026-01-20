from typing import Dict, Optional, Union, Any
from pydantic import BaseModel, Field
from ankitools.core.config import BaseConfig

class ClozeFields(BaseModel):
    word: str = "Expression"
    sentence: str = "Sentence"
    
    model_config = {"extra": "allow"}

class ClozeConfigSchema(BaseModel):
    default_deck: Optional[str] = None
    default_model: Optional[str] = None
    fields: ClozeFields = Field(default_factory=ClozeFields)

class ClozeTransformConfig(BaseConfig):
    def __init__(self, config_input: Union[str, Dict[str, Any], None] = None):
        # Allow injecting raw data for testing
        if isinstance(config_input, dict):
            self.data = config_input
            # We skip BaseConfig.__init__ file loading logic
        else:
            super().__init__(config_input)

        section = self.get_section('cloze_transform')
        self._schema = ClozeConfigSchema(**section)

    @property
    def default_deck(self) -> Optional[str]:
        return self._schema.default_deck

    @property
    def default_model(self) -> Optional[str]:
        return self._schema.default_model

    @property
    def fields(self) -> ClozeFields:
        return self._schema.fields
