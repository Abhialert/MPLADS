"""Phase 3.6 snapshot models — extends existing DB schema (no rebuild)."""
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class SourceSnapshot(Base):
    """Immutable snapshot from a source ingestion (Section 3)."""
    __tablename__ = "source_snapshots"

    snapshot_id = Column(String, primary_key=True, index=True)
    source_id = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    captured_at = Column(DateTime, nullable=False)
    source_period_start = Column(String, nullable=True)
    source_period_end = Column(String, nullable=True)
    record_count = Column(Integer, nullable=False)
    schema_fingerprint = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    parser_version = Column(String, nullable=False)
    ingestion_version = Column(String, nullable=False)
    status = Column(String, nullable=False, default="COMPLETE")
    provenance = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class RecordVersion(Base):
    """Record-level version history (Section 6)."""
    __tablename__ = "record_versions"

    version_id = Column(String, primary_key=True, index=True)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    snapshot_id = Column(String, ForeignKey("source_snapshots.snapshot_id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    observed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    fields_json = Column(JSON, nullable=True)
    source_work_id = Column(String, nullable=True)
    previous_version_id = Column(String, nullable=True)
    identity_confidence = Column(String, nullable=False, default="HIGH")  # HIGH, MEDIUM, LOW, UNAVAILABLE

class SnapshotComparison(Base):
    """Snapshot comparison result (Section 7-8)."""
    __tablename__ = "snapshot_comparisons"

    comparison_id = Column(String, primary_key=True, index=True)
    before_snapshot_id = Column(String, ForeignKey("source_snapshots.snapshot_id"), nullable=False)
    after_snapshot_id = Column(String, ForeignKey("source_snapshots.snapshot_id"), nullable=False)
    comparison_version = Column(String, nullable=False)
    identity_version = Column(String, nullable=False)
    normalization_version = Column(String, nullable=False)
    records_before = Column(Integer, nullable=True)
    records_after = Column(Integer, nullable=True)
    records_unchanged = Column(Integer, nullable=True)
    records_added = Column(Integer, nullable=True)
    records_removed = Column(Integer, nullable=True)
    records_modified = Column(Integer, nullable=True)
    fields_changed = Column(Integer, nullable=True)
    identity_uncertainty = Column(Integer, nullable=True)
    match_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class FieldChange(Base):
    """Field-level change between snapshots (Section 7)."""
    __tablename__ = "field_changes"

    change_id = Column(String, primary_key=True, index=True)
    comparison_id = Column(String, ForeignKey("snapshot_comparisons.comparison_id"), nullable=False)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    field_name = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    change_type = Column(String, nullable=False)  # ADDED, REMOVED, MODIFIED, UNCHANGED, NORMALIZATION_ONLY, UNKNOWN
    provenance_before = Column(String, nullable=True)
    provenance_after = Column(String, nullable=True)
    identity_confidence = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
