from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional

class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)


class NoteOut(BaseModel):
    id: int
    content: str = Field(..., min_length=1)
    created_at: str

class ExtractRequest(BaseModel):
    # Keep validation aligned with current router behavior:
    # the endpoint strips/validates and returns HTTP 400 for empty text.
    text: str = ""
    save_note: bool = False

class ActionItemOut(BaseModel):
    id: int
    text: str

class ExtractResponse(BaseModel):
    note_id: Optional[int]
    items: List[ActionItemOut]