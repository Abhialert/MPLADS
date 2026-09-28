"""Phase 3.7 — Cross-source reconciliation engine.

Uses ONLY sources that actually exist. Does not split MPLADS.csv into
fake Source A / Source B. Does not fabricate conflicts.

With one legitimate source, runs same-source identity consistency
(duplicate composite keys, exact-id uniqueness) and reports:

    CROSS_SOURCE_DEPTH = INSUFFICIENT

Match methods: EXACT_ID | DETERMINISTIC_COMPOSITE | UNMATCHED | AMBIGUOUS
Never overmatches. Prefer UNMATCHED / AMBIGUOUS over a false join.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import time
import unicodedata
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

CSV_PATH = "C:/Users/ABHISHEK/Desktop/MPLAD_Integrity_Engine/data/input/MPLADS.csv"
SOURCE_ID = "src-mplads-csv-60359"
PROVENANCE_CLASS = "THIRD_PARTY_DERIVED"
# CSV is a user-provided export of MPLADS dashboard data — not an official
# live API dump. Do not upgrade provenance to OFFICIAL_PRIMARY.


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    t = unicodedata.normalize("NFC", str(value)).strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def normalize_amount(value: Any) -> Optional[float]:
    if value is None or str(value).strip() in ("", "-", "na", "n/a", "null", "none"):
        return None
    cleaned = str(value).replace(",", "").replace("₹", "").replace("Rs", "").replace("INR", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_date(value: Any) -> Optional[str]:
    if not value:
        return None
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return s or None


def composite_identity(row: Dict[str, str]) -> str:
    """Deterministic composite key from stable observed fields.
    CSV has no unique_work_number; do not invent one.
    """
    parts = [
        normalize_text(row.get("MP NAME")),
        normalize_text(row.get("CONSTITUENCY")),
        normalize_text(row.get("STATE")),
        normalize_text(row.get("WORK")),
        normalize_date(row.get("RECOMMENDED DATE")) or "",
        str(normalize_amount(row.get("ALLOCATION AMOUNT")) or ""),
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def record_id(index: int, row: Dict[str, str]) -> str:
    return f"{SOURCE_ID}-r{index:06d}"


def load_csv(path: str = CSV_PATH) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def artifact_hash(path: str = CSV_PATH) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_same_source_identity(path: str = CSV_PATH) -> Dict[str, Any]:
    """Same-source identity consistency on the one real CSV.

    Groups records by deterministic composite identity.
    - unique composite key  -> consistent identity (not a cross-source match)
    - duplicate composite   -> AMBIGUOUS (do not auto-merge)
    Never claims these are two independent sources.
    """
    start = time.time()
    rows = load_csv(path)
    groups: Dict[str, List[Tuple[int, Dict[str, str]]]] = defaultdict(list)
    for i, row in enumerate(rows):
        groups[composite_identity(row)].append((i, row))

    unique_keys = 0
    ambiguous_groups = 0
    ambiguous_records = 0
    duplicate_examples: List[Dict[str, Any]] = []

    for key, members in groups.items():
        if len(members) == 1:
            unique_keys += 1
        else:
            ambiguous_groups += 1
            ambiguous_records += len(members)
            if len(duplicate_examples) < 5:
                sample = members[0][1]
                duplicate_examples.append({
                    "composite_key": key,
                    "count": len(members),
                    "match_method": "DETERMINISTIC_COMPOSITE",
                    "match_confidence": "AMBIGUOUS",
                    "mp_name": sample.get("MP NAME"),
                    "constituency": sample.get("CONSTITUENCY"),
                    "work": (sample.get("WORK") or "")[:80],
                    "recommended_date": sample.get("RECOMMENDED DATE"),
                    "allocation": sample.get("ALLOCATION AMOUNT"),
                    "note": "Multiple rows share the same composite identity. Not auto-merged.",
                })

    elapsed = round(time.time() - start, 3)
    return {
        "cross_source_depth": "INSUFFICIENT",
        "cross_source_validation": "INSUFFICIENT_SOURCE_DEPTH",
        "sources": [
            {
                "source_id": SOURCE_ID,
                "source_name": "MPLADS.csv (user-provided dashboard export)",
                "provenance_class": PROVENANCE_CLASS,
                "source_url": "https://mplads.mospi.gov.in/digigov/dashboard.html",
                "record_count": len(rows),
                "artifact_hash": artifact_hash(path),
                "parser_version": "v1.0-semicolon-csv",
                "schema_fingerprint": "MPLADS_CSV_15_COLS",
                "limitations": (
                    "User-provided export. Not a live official API dump. "
                    "Do not treat as OFFICIAL_PRIMARY. No unique_work_number in this schema."
                ),
            }
        ],
        "second_source": None,
        "matching_method": "DETERMINISTIC_COMPOSITE (same-source identity consistency only)",
        "records_processed": len(rows),
        "confirmed_cross_source_matches": 0,
        "ambiguous_composite_groups": ambiguous_groups,
        "ambiguous_records": ambiguous_records,
        "unique_composite_keys": unique_keys,
        "unmatched_cross_source": len(rows),
        "field_comparisons_cross_source": 0,
        "real_conflicts_cross_source": 0,
        "agreement_rate_cross_source": None,
        "conflict_count_by_type": {},
        "duplicate_identity_examples": duplicate_examples,
        "processing_seconds": elapsed,
        "evidence_lineage": (
            "SOURCE -> SOURCE_RECORD -> COMPOSITE_IDENTITY. "
            "No SOURCE_B node exists. Graph edges for cross-source matches are not created."
        ),
        "limitations": [
            "Only one legitimate work-level source is available (MPLADS.csv, 60359 records).",
            "DataSheet_MPLADS.pdf is a datasheet PDF, not a work-level record source — not used as Source B.",
            "Dataful datasets remain PENDING_DOWNLOAD and were not ingested.",
            "No second source was manufactured by splitting the CSV.",
            "No unique_work_number field exists in this export; identity is composite.",
            "Duplicate composite keys are AMBIGUOUS, not confirmed matches.",
            "RECONCILIATION is not added as a HIGH review-priority family without a second source.",
        ],
        "real_data_label": "REAL_MPLADS_60359",
        "note": (
            "Architecture implemented. Cross-source matching is not validated. "
            "When a second independent work-level source is ingested, run compare() "
            "with EXACT_ID first, then DETERMINISTIC_COMPOSITE, never weak fuzzy as exact."
        ),
    }


def compare_fields(a: Dict[str, Any], b: Dict[str, Any], field_map: Dict[str, Tuple[str, str]]) -> List[Dict[str, Any]]:
    """Field-level AGREE/DISAGREE. Only fields present in both. Unused until Source B exists."""
    results = []
    for canonical, (ka, kb) in field_map.items():
        va_raw = a.get(ka)
        vb_raw = b.get(kb)
        if (va_raw is None or str(va_raw).strip() == "") and (vb_raw is None or str(vb_raw).strip() == ""):
            cls = "NOT_COMPARABLE"
            na = nb = None
        elif va_raw is None or str(va_raw).strip() == "":
            cls = "MISSING_IN_SOURCE_A"
            na, nb = None, normalize_text(vb_raw)
        elif vb_raw is None or str(vb_raw).strip() == "":
            cls = "MISSING_IN_SOURCE_B"
            na, nb = normalize_text(va_raw), None
        else:
            if canonical.endswith("amount"):
                na, nb = normalize_amount(va_raw), normalize_amount(vb_raw)
            elif "date" in canonical:
                na, nb = normalize_date(va_raw), normalize_date(vb_raw)
            else:
                na, nb = normalize_text(va_raw), normalize_text(vb_raw)
            cls = "AGREE" if na == nb else "DISAGREE"
        results.append({
            "field_name": canonical,
            "classification": cls,
            "value_a_raw": None if va_raw is None else str(va_raw),
            "value_b_raw": None if vb_raw is None else str(vb_raw),
            "value_a_normalized": None if na is None else str(na),
            "value_b_normalized": None if nb is None else str(nb),
            "evidence_quality": "DERIVED" if cls in ("AGREE", "DISAGREE") else "UNAVAILABLE",
        })
    return results


def persist_run(result: Dict[str, Any], db_path: str) -> None:
    """Persist reconciliation run + registered source. Does not invent matches."""
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS reconciliation_sources (
            source_id TEXT PRIMARY KEY, source_name TEXT, provenance_class TEXT,
            source_url TEXT, retrieval_time TEXT, artifact_hash TEXT,
            parser_version TEXT, schema_fingerprint TEXT, record_count INTEGER,
            snapshot_id TEXT, status TEXT, limitations TEXT, created_at TEXT
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS reconciliation_runs (
            run_id TEXT PRIMARY KEY, source_a_id TEXT, source_b_id TEXT,
            records_a INTEGER, records_b INTEGER, confirmed_matches INTEGER,
            ambiguous_matches INTEGER, unmatched_records INTEGER,
            field_agreements INTEGER, field_disagreements INTEGER, conflict_count INTEGER,
            processing_seconds REAL, cross_source_depth TEXT, limitations TEXT, created_at TEXT
        )"""
    )
    src = result["sources"][0]
    now = datetime.utcnow().isoformat()
    cur.execute("SELECT 1 FROM reconciliation_sources WHERE source_id=?", (src["source_id"],))
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO reconciliation_sources VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                src["source_id"], src["source_name"], src["provenance_class"],
                src["source_url"], now, src["artifact_hash"], src["parser_version"],
                src["schema_fingerprint"], src["record_count"], "SNAP-REAL-60359-001",
                "REGISTERED", src["limitations"], now,
            ),
        )
    run_id = "RECON-RUN-SINGLE-SOURCE-" + datetime.utcnow().strftime("%Y%m%d")
    cur.execute("DELETE FROM reconciliation_runs WHERE run_id=?", (run_id,))
    cur.execute(
        "INSERT INTO reconciliation_runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            run_id, SOURCE_ID, None, result["records_processed"], 0,
            result["confirmed_cross_source_matches"], result["ambiguous_composite_groups"],
            result["unmatched_cross_source"], 0, 0, 0, result["processing_seconds"],
            result["cross_source_depth"], json.dumps(result["limitations"]), now,
        ),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    result = run_same_source_identity()
    db = "C:/Users/ABHISHEK/Desktop/MPLAD_Integrity_Engine/data/mplad_integrity.db"
    persist_run(result, db)
    print(json.dumps({k: v for k, v in result.items() if k != "duplicate_identity_examples"}, indent=2, default=str))
    print("--- AMBIGUOUS COMPOSITE EXAMPLES (real rows, not fabricated) ---")
    print(json.dumps(result["duplicate_identity_examples"], indent=2, default=str))
