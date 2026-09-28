"""Phase 3.7 — Cross-source reconciliation models.
Reuse existing ReconciliationConflict in works.py; these tables add match,
source registry, evidence-graph edges, and field-level comparison results.
No fabricated sources. Provenance classes are explicit."""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.sqlite import JSON
from .database import Base


class ReconciliationSource(Base):
    """Registered source with explicit provenance (Section 3)."""
    __tablename__ = "reconciliation_sources"

    source_id = Column(String, primary_key=True, index=True)
    source_name = Column(String, nullable=False)
    provenance_class = Column(String, nullable=False)
    # OFFICIAL_PRIMARY | GOVERNMENT_SECONDARY | THIRD_PARTY_DERIVED | USER_PROVIDED | UNKNOWN
    source_url = Column(String, nullable=True)
    retrieval_time = Column(DateTime, nullable=True)
    artifact_hash = Column(String, nullable=True)
    parser_version = Column(String, nullable=True)
    schema_fingerprint = Column(String, nullable=True)
    record_count = Column(Integer, nullable=True)
    snapshot_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="REGISTERED")
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class CanonicalEntity(Base):
    """Canonical work/entity that source records may link to (Section 4)."""
    __tablename__ = "canonical_entities"

    entity_id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False, default="WORK")
    identity_method = Column(String, nullable=False)
    identity_confidence = Column(String, nullable=False, default="MEDIUM")
    identity_key = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SourceMatch(Base):
    """Cross-source or intra-source link (Section 5). Prefer UNMATCHED/AMBIGUOUS over false join."""
    __tablename__ = "source_matches"

    match_id = Column(String, primary_key=True, index=True)
    source_a_id = Column(String, nullable=False, index=True)
    source_b_id = Column(String, nullable=False, index=True)
    source_a_record_id = Column(String, nullable=False)
    source_b_record_id = Column(String, nullable=False)
    canonical_entity_id = Column(String, ForeignKey("canonical_entities.entity_id"), nullable=True, index=True)
    match_method = Column(String, nullable=False)
    # EXACT_ID | DETERMINISTIC_COMPOSITE | PROBABILISTIC | UNMATCHED | AMBIGUOUS
    match_confidence = Column(String, nullable=False)
    match_evidence = Column(Text, nullable=True)
    matched_fields_json = Column(JSON, nullable=True)
    unmatched_fields_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class FieldReconciliation(Base):
    """Field-level AGREE/DISAGREE for a match (Section 7)."""
    __tablename__ = "field_reconciliations"

    recon_id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("source_matches.match_id"), nullable=False, index=True)
    field_name = Column(String, nullable=False)
    classification = Column(String, nullable=False)
    # AGREE | DISAGREE | MISSING_IN_SOURCE_A | MISSING_IN_SOURCE_B | NOT_COMPARABLE
    value_a_raw = Column(String, nullable=True)
    value_b_raw = Column(String, nullable=True)
    value_a_normalized = Column(String, nullable=True)
    value_b_normalized = Column(String, nullable=True)
    evidence_quality = Column(String, nullable=True)  # OBSERVED | DERIVED | SECONDARY | UNAVAILABLE
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class EvidenceGraphEdge(Base):
    """Stored graph edge backed by actual evidence (Section 10). Not decorative."""
    __tablename__ = "evidence_graph_edges"

    edge_id = Column(String, primary_key=True, index=True)
    from_node_type = Column(String, nullable=False)
    from_node_id = Column(String, nullable=False, index=True)
    to_node_type = Column(String, nullable=False)
    to_node_id = Column(String, nullable=False, index=True)
    relation = Column(String, nullable=False)
    evidence_ref = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ReconciliationRun(Base):
    """One reconciliation execution (performance + depth reporting)."""
    __tablename__ = "reconciliation_runs"

    run_id = Column(String, primary_key=True, index=True)
    source_a_id = Column(String, nullable=False)
    source_b_id = Column(String, nullable=True)
    records_a = Column(Integer, nullable=True)
    records_b = Column(Integer, nullable=True)
    confirmed_matches = Column(Integer, nullable=True)
    ambiguous_matches = Column(Integer, nullable=True)
    unmatched_records = Column(Integer, nullable=True)
    field_agreements = Column(Integer, nullable=True)
    field_disagreements = Column(Integer, nullable=True)
    conflict_count = Column(Integer, nullable=True)
    processing_seconds = Column(Float, nullable=True)
    cross_source_depth = Column(String, nullable=False, default="INSUFFICIENT")
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
