#!/usr/bin/env python3
"""
validator.py

Simple validation backend.

Directory structure:

data/
    source/
        node-33063987.geojson
    text/
        33063987.txt
    parsed/
        33063987.txt

validation/
    33063987.json

Run:

    pip install fastapi uvicorn
    uvicorn validator:app --reload

Open:

    http://localhost:8000/
"""

from pathlib import Path
import json
import re
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ----------------------------------------------------------------------

BASE = Path(__file__).parent

SOURCE_DIR = BASE / "data" / "source"
TEXT_DIR = BASE / "data" / "text"
PARSED_DIR = BASE / "data" / "parsed"

VALIDATION_DIR = BASE / "validation"
VALIDATION_DIR.mkdir(exist_ok=True)

INDEX_HTML = BASE / "validator.html"

# ----------------------------------------------------------------------

app = FastAPI(title="LLM Validation Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------


class Validation(BaseModel):
    id: int
    status: str
    comment: str = ""


# ----------------------------------------------------------------------


def extract_id(filename: str) -> Optional[int]:
    m = re.search(r"(\d+)", filename)
    if not m:
        return None
    return int(m.group(1))


# ----------------------------------------------------------------------


def all_ids() -> List[int]:
    ids = []

    for f in SOURCE_DIR.glob("*.geojson"):
        i = extract_id(f.name)

        if i is None:
            continue

        if not (TEXT_DIR / f"{i}.txt").exists():
            continue

        if not (PARSED_DIR / f"{i}.txt").exists():
            continue

        ids.append(i)

    return sorted(ids)


# ----------------------------------------------------------------------


IDS = all_ids()

# ----------------------------------------------------------------------


def validation_path(i: int):
    return VALIDATION_DIR / f"{i}.json"


def is_validated(i: int):
    return validation_path(i).exists()


# ----------------------------------------------------------------------


def load_geojson(i: int):

    filename = SOURCE_DIR / f"node-{i}.geojson"

    if not filename.exists():
        raise HTTPException(404)

    with open(filename, encoding="utf8") as f:
        return json.load(f)


# ----------------------------------------------------------------------


def load_text(i: int):

    return (TEXT_DIR / f"{i}.txt").read_text(
        encoding="utf8",
        errors="ignore",
    )


# ----------------------------------------------------------------------


def load_parsed(i: int):

    return (PARSED_DIR / f"{i}.txt").read_text(
        encoding="utf8",
        errors="ignore",
    ).strip()


# ----------------------------------------------------------------------


def find_evidence(text: str):

    keywords = [
        "öffnungszeiten",
        "opening hours",
        "opening",
        "hours",
    ]

    lower = text.lower()

    for k in keywords:

        pos = lower.find(k)

        if pos == -1:
            continue

        start = max(0, pos - 250)
        end = min(len(text), pos + 600)

        return text[start:end]

    return text[:800]


# ----------------------------------------------------------------------


@app.get("/")
def index():
    return FileResponse(INDEX_HTML)


# ----------------------------------------------------------------------


@app.get("/api/stats")
def stats():

    validated = sum(is_validated(i) for i in IDS)

    return {
        "total": len(IDS),
        "validated": validated,
        "remaining": len(IDS) - validated,
    }


# ----------------------------------------------------------------------


@app.get("/api/next")
def next_record():

    for i in IDS:

        if not is_validated(i):

            geo = load_geojson(i)

            return {
                "id": i,
                "geojson": geo,
                "text": load_text(i),
                "parsed": load_parsed(i),
                "evidence": find_evidence(load_text(i)),
            }

    return None


# ----------------------------------------------------------------------


@app.get("/api/record/{record_id}")
def record(record_id: int):

    geo = load_geojson(record_id)

    return {
        "id": record_id,
        "geojson": geo,
        "text": load_text(record_id),
        "parsed": load_parsed(record_id),
        "evidence": find_evidence(load_text(record_id)),
    }


# ----------------------------------------------------------------------


@app.get("/api/list")
def list_records():

    result = []

    for i in IDS:

        state = "pending"

        p = validation_path(i)

        if p.exists():

            with open(p) as f:
                state = json.load(f)["status"]

        result.append(
            {
                "id": i,
                "status": state,
            }
        )

    return result


# ----------------------------------------------------------------------


@app.post("/api/save")
def save(v: Validation):

    if v.status not in [
        "correct",
        "wrong",
        "partial",
        "unsure",
    ]:
        raise HTTPException(400, "invalid status")

    with open(validation_path(v.id), "w", encoding="utf8") as f:

        json.dump(
            {
                "id": v.id,
                "status": v.status,
                "comment": v.comment,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    return {"ok": True}


# ----------------------------------------------------------------------


@app.get("/api/validation/{record_id}")
def validation(record_id: int):

    p = validation_path(record_id)

    if not p.exists():
        return None

    with open(p, encoding="utf8") as f:
        return json.load(f)