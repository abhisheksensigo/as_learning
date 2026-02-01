import os
import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_llm_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items_llm(text)
    lowered = [i.strip().lower() for i in items]
    assert "set up database" in lowered
    assert "implement api extract endpoint" in lowered
    assert "write tests" in lowered


def test_extract_llm_keyword_prefixed_lines():
    text = """
    Notes:
    todo: email the client
    action: update the docs
    next: verify deployment
    This is just narrative.
    """.strip()

    items = extract_action_items_llm(text)
    lowered = [i.strip().lower() for i in items]
    assert "email the client" in lowered
    assert "update the docs" in lowered
    assert "verify deployment" in lowered


def test_extract_empty_notes_returns_empty_list():
    text = ""
    assert extract_action_items_llm(text) == []
    assert extract_action_items_llm("   \n\n\t  ") == []
