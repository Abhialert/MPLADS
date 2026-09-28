"""Phase 3.5 — ML Evidence Schema + Framework (honest approach, no synthetic scores).
Framework designed; actual Isolation Forest requires sklearn/numpy (unavailable in this environment).
No synthetic data, no fraud claims, no fabricated accuracy."""
from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base  # import from project

class MLModelMetadata(Base):
    """Model governance — Section 13 (reproducibility)."""
    __tablename__ = "ml_model_metadata"

    model_id = Column(String, primary_key=True, index=True)
    model_name = Column(String, nullable=False)
    algorithm = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    source_snapshot_id = Column(String, nullable=True)
    feature_version = Column(String, nullable=False)
    dataset_version = Column(String, nullable=False)
    record_count = Column(Integer, nullable=False)
    feature_count = Column(Integer, nullable=False)
    random_seed = Column(Integer, nullable=True)
    hyperparameters_json = Column(JSON, nullable=True)
    model_status = Column(String, nullable=False, default="PREPARED")  # PREPARED | EXECUTED | UNAVAILABLE_DEPS
    limitations = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class MLEvidence(Base):
    """Evidence object for ML findings — Section 7 (persisted)."""
    __tablename__ = "ml_evidence"

    evidence_id = Column(String, primary_key=True, index=True)
    finding_id = Column(String, nullable=True)  # links to aggregated finding if ML contributes
    work_id = Column(String, nullable=True)
    model_id = Column(String, nullable=False, index=True)
    detector_family = Column(String, nullable=False, default="ML")
    detector_version = Column(String, nullable=False)
    feature_set_version = Column(String, nullable=False)
    source_snapshot_id = Column(String, nullable=False)

    # Raw and processed outputs
    raw_model_output = Column(Float, nullable=True)
    normalized_output = Column(Float, nullable=True)
    outlier_flag = Column(Boolean, nullable=True)

    # Evidence documentation
    feature_context_json = Column(JSON, nullable=True)  # actual feature values
    feature_groups_json = Column(JSON, nullable=True)  # which groups contributed
    explanation_notes = Column(Text, nullable=True)

    # Quality and reproducibility
    evidence_quality = Column(String, nullable=True)  # HIGH / MEDIUM / LOW / NONE (if unavailable)
    limitations = Column(Text, nullable=True)
    reproducible_snapshot = Column(String, nullable=True)

    # Status tracking — Section 8 (ML as supplementary only when no sklearn)
    contribution_type = Column(String, nullable=False, default="SUPPLEMENTARY")
    # SUPPLEMENTARY: framework ready but not executed due to dependency unavailability
    # PRIMARY: executed and contributes independently

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class MLContributionAnalysis(Base):
    """Comparison of ML results against existing detector families — Section 5 (model contribution)."""
    __tablename__ = "ml_contribution_analysis"

    analysis_id = Column(String, primary_key=True, index=True)
    model_id = Column(String, nullable=False)
    dataset_version = Column(String, nullable=False)
    execution_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Overlap statistics
    total_works = Column(Integer, nullable=False)
    ml_outlier_count = Column(Integer, nullable=False)
    overlap_with_financial_count = Column(Integer, nullable=False)
    overlap_with_peer_count = Column(Integer, nullable=False)
    overlap_with_similarity_count = Column(Integer, nullable=False)
    overlap_with_temporal_count = Column(Integer, nullable=False)
    ml_only_count = Column(Integer, nullable=False)
    overlap_percentage = Column(Float, nullable=True)

    # Assessment
    contribution_assessment = Column(String, nullable=True)
    # Example values: "MEANINGFUL" | "REDUNDANT" | "INSUFFICIENT_DEPS" | "PENDING_EXECUTION"
    assessment_rationale = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)

    # Reproducibility
    feature_version = Column(String, nullable=False)
    random_seed = Column(Integer, nullable=True)
