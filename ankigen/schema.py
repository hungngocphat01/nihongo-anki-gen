from typing import Optional, List
from pydantic import BaseModel, Field

class Entry(BaseModel):
    """Pydantic model for structured LLM output"""
    vocab: str = Field(description="The word itself")
    furigana: str = Field(description="The furigana for the word")
    meaning: str = Field(description="The meaning of the word (in the chosen sense)")
    example: str = Field(description="Example sentence using the word")
    example_trans: str = Field(description="Translation for the example sentence")
    kind: str = Field(description="Vocabulary type: 'vocab' or 'collocation'")
    hanviet: Optional[str] = Field(default=None, description="Han-viet pronunciation")
    
class ModelOutput(BaseModel):
    output: List[Entry] = Field(description="List of output objects")
