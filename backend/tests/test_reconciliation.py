"""Phase 3.7 tests: normalization, composite identity, no overmatch, no fake Source B."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.cross_source_reconciliation import (
    normalize_amount,
    normalize_text,
    normalize_date,
    composite_identity,
    compare_fields,
    SOURCE_ID,
    PROVENANCE_CLASS,
)


def test_amount_normalization_indian_format():
    assert normalize_amount("₹4,00,000") == 400000.0
    assert normalize_amount("400000") == 400000.0
    assert normalize_amount("") is None


def test_text_normalization():
    assert normalize_text("  Road  Work ") == "road work"


def test_date_normalization():
    assert normalize_date("2024-03-04") == "2024-03-04"
    assert normalize_date("04-03-2024") == "2024-03-04"


def test_composite_identity_deterministic():
    row = {
        "MP NAME": "Manoj Rajoria",
        "CONSTITUENCY": "KARAULI-DHOLPUR(SC)",
        "STATE": "Rajasthan",
        "WORK": "NA - Installing community drinking water plants",
        "RECOMMENDED DATE": "2024-03-04",
        "ALLOCATION AMOUNT": "100000",
    }
    a = composite_identity(row)
    b = composite_identity(row)
    assert a == b
    assert len(a) == 24


def test_composite_identity_differs_when_amount_differs():
    row_a = {
        "MP NAME": "X", "CONSTITUENCY": "Y", "STATE": "Z",
        "WORK": "hall", "RECOMMENDED DATE": "2024-01-01", "ALLOCATION AMOUNT": "100000",
    }
    row_b = dict(row_a)
    row_b["ALLOCATION AMOUNT"] = "200000"
    assert composite_identity(row_a) != composite_identity(row_b)


def test_compare_fields_agree_after_normalization():
    a = {"ALLOCATION AMOUNT": "₹1,00,000"}
    b = {"ALLOCATION AMOUNT": "100000"}
    out = compare_fields(a, b, {"allocation_amount": ("ALLOCATION AMOUNT", "ALLOCATION AMOUNT")})
    assert out[0]["classification"] == "AGREE"
    assert out[0]["value_a_raw"] != out[0]["value_b_raw"]


def test_compare_fields_disagree():
    a = {"STATUS": "Completed"}
    b = {"STATUS": "Ongoing"}
    out = compare_fields(a, b, {"status": ("STATUS", "STATUS")})
    assert out[0]["classification"] == "DISAGREE"


def test_compare_fields_missing():
    a = {"STATUS": ""}
    b = {"STATUS": "Ongoing"}
    out = compare_fields(a, b, {"status": ("STATUS", "STATUS")})
    assert out[0]["classification"] == "MISSING_IN_SOURCE_A"


def test_provenance_not_upgraded():
    assert PROVENANCE_CLASS == "THIRD_PARTY_DERIVED"
    assert SOURCE_ID.startswith("src-mplads")


def test_no_source_b_constant():
    from app.services import cross_source_reconciliation as m
    assert not hasattr(m, "SOURCE_B_ID")
