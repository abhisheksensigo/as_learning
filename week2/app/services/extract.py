from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from dotenv import load_dotenv

load_dotenv()

try:
    # Optional dependency: keep deterministic extraction usable without Ollama installed.
    from ollama import chat as ollama_chat
except ModuleNotFoundError:  # pragma: no cover
    ollama_chat = None

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "action item:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str) -> List[str]:
    """
    LLM-powered action item extraction using Ollama.

    Goal: mimic `extract_action_items()` output shape and post-processing exactly.
    This is a scaffold: prompt/model selection can be refined, but callers should
    already get a stable List[str] and safe fallback behavior.
    """
    # TODO: make model configurable (env var / config)
    model = os.getenv("OLLAMA_MODEL", "llama3.2")

    system_prompt = (
        "You extract action items (TODOs) from text.\n"
        "Return ONLY valid JSON: an array of strings.\n"
        "Each string should be a short action item; no numbering;\n"
        " no extra keys.\n"
        "Ensure that the strings are in the same format as the input text and strings match. \n"
        "Don't summarize the strings."
    )

    try:
        if ollama_chat is None:
            raise ModuleNotFoundError("ollama is not installed")

        resp = ollama_chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        content = (resp.get("message") or {}).get("content", "")

        # Expect a JSON array of strings. If the model returns prose, parsing fails
        # and we fall back to the deterministic implementation below.
        parsed: Any = json.loads(content)
        if not isinstance(parsed, list):
            raise ValueError("Ollama response is not a JSON array")

        extracted: List[str] = []
        for item in parsed:
            if not isinstance(item, str):
                continue
            s = item.strip()
            if not s:
                continue
            extracted.append(s)

        # Apply the SAME dedupe semantics as `extract_action_items()`.
        seen: set[str] = set()
        unique: List[str] = []
        for item in extracted:
            lowered = item.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            unique.append(item)

        # If the model returns nothing useful, mimic the base function behavior.
        return unique or extract_action_items(text)
    except Exception:
        # Safe fallback: preserve exact behavior even if Ollama isn't running.
        return extract_action_items(text)


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "todo",
        "action",
        "next",   
        "investigate",
    }
    return first.lower() in imperative_starters


