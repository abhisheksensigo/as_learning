from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from .. import db
from ..services.extract import extract_action_items, extract_action_items_llm

try:
    from ..schemas import ExtractRequest, ExtractResponse
except ImportError:  # pragma: no cover
    # Temporary local fallback so this router can work before schemas are added.
    # (Per instructions, we are not modifying other files in this step.)
    from pydantic import BaseModel

    class ExtractRequest(BaseModel):
        text: str = ""
        save_note: bool = False

    class ExtractResponse(BaseModel):
        note_id: Optional[int]
        items: List[Dict[str, Any]]




router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    text = str(getattr(payload, "text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if bool(getattr(payload, "save_note", False)):
        note_id = db.insert_note(text)

    items = extract_action_items(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[{"id": i, "text": t} for i, t in zip(ids, items)],
    )


@router.post("/extract_llm", response_model=ExtractResponse)
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    text = str(getattr(payload, "text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if bool(getattr(payload, "save_note", False)):
        note_id = db.insert_note(text)

    items = extract_action_items_llm(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[{"id": i, "text": t} for i, t in zip(ids, items)],
    )


@router.get("")
def list_all(note_id: Optional[int] = None) -> List[Dict[str, Any]]:
    rows = db.list_action_items(note_id=note_id)
    return [
        {
            "id": r["id"],
            "note_id": r["note_id"],
            "text": r["text"],
            "done": bool(r["done"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


@router.post("/{action_item_id}/done")
def mark_done(action_item_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    done = bool(payload.get("done", True))
    db.mark_action_item_done(action_item_id, done)
    return {"id": action_item_id, "done": done}


