## Week 2 — Action Item Extractor (FastAPI + SQLite + Ollama)

A minimal web app that turns free-form meeting notes into a checklist of actionable items. It supports both:

- A **heuristic extractor** (fast, deterministic)
- An **LLM-powered extractor** via **Ollama** (local model inference)

The Week 2 project lives in `week2/` and includes a tiny HTML frontend served by the FastAPI app.

## Tech stack

- **Backend**: FastAPI, Pydantic
- **Server**: Uvicorn
- **Database**: SQLite (file-backed)
- **LLM**: Ollama (local) + `ollama` Python client
- **Tests**: pytest

## Setup (conda + Poetry)

From the repository root:

```bash
# 1) Create/activate a conda environment
conda create -n cs146s python=3.11 -y
conda activate cs146s

# 2) Install Poetry (if you don't already have it)
pip install poetry

# 3) Install dependencies
poetry install
```

## Run the server

From the repository root:

```bash
poetry run uvicorn week2.app.main:app --reload
```

Then open the UI at `http://127.0.0.1:8000/`.

## API endpoints

### POST `/action-items/extract`

Extract action items using the **heuristic** extractor.

- **Request body**:

```json
{ "text": "your notes here", "save_note": true }
```

- **Response body**:

```json
{
  "note_id": 123,
  "items": [{ "id": 1, "text": "Set up database" }]
}
```

### POST `/action-items/extract_llm`

Extract action items using the **LLM** extractor (Ollama-backed).

- **Request body** (same as `/extract`):

```json
{ "text": "your notes here", "save_note": true }
```

- **Response body** (same shape as `/extract`):

```json
{
  "note_id": 123,
  "items": [{ "id": 1, "text": "Set up database" }]
}
```

### GET `/notes`

List all saved notes.

- **Response body**:

```json
[
  { "id": 123, "content": "raw note text", "created_at": "2026-01-28 12:34:56" }
]
```

### POST `/notes`

Create a new note.

- **Request body**:

```json
{ "content": "raw note text" }
```

- **Response body**:

```json
{ "id": 123, "content": "raw note text", "created_at": "2026-01-28 12:34:56" }
```

## Run tests (pytest)

The Week 2 tests live in `week2/tests/`. Run them from the `week2/` directory:

```bash
cd week2
poetry run pytest -q
```

## Ollama notes / requirements

- **Install Ollama**: follow the instructions at `https://ollama.com/`.
- **Start the Ollama server** (if it isn’t already running): `ollama serve`
- **Pull a model** (example): `ollama pull llama3.2`
- **Select the model** (optional): set `OLLAMA_MODEL` (default is `llama3.2`)

```bash
export OLLAMA_MODEL="llama3.2"
```

The `/action-items/extract_llm` endpoint calls the Ollama-backed extraction function. If Ollama (or the Python client) is unavailable at runtime, the app may fall back to the deterministic extractor.

