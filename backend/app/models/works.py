from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Work(Base):
    __tablename__ = "works"

    work_id = Column(String, primary_key=True, index=True)
    source_work_id = Column(String, nullable=True)
    data_source = Column(String, nullable=False, default="REAL_ESAKSHI")

    mp_name = Column(String, nullable=True)
    mp_type = Column(String, nullable=True)
    constituency = Column(String, nullable=True)
    state = Column(String, nullable=True)
    district = Column(String, nullable=True)

    financial_year = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    work_description = Column(Text, nullable=True)
    implementing_agency = Column(String, nullable=True)
    contractor_name = Column(String, nullable=True)

    location_text = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    is_within_constituency = Column(Boolean, nullable=True)
    is_sc_area = Column(Boolean, nullable=True)
    is_st_area = Column(Boolean, nullable=True)

    beneficiary_type = Column(String, nullable=True)
    asset_owner_type = Column(String, nullable=True)

    recommended_amount = Column(Float, nullable=True)
    sanctioned_amount = Column(Float, nullable=True)
    actual_expenditure = Column(Float, nullable=True)
    total_paid = Column(Float, nullable=True)

    recommendation_date = Column(DateTime, nullable=True)
    sanction_date = Column(DateTime, nullable=True)
    ia_assignment_date = Column(DateTime, nullable=True)
    expected_completion_date = Column(DateTime, nullable=True)
    actual_completion_date = Column(DateTime, nullable=True)
    final_payment_date = Column(DateTime, nullable=True)
    marked_complete_date = Column(DateTime, nullable=True)

    status = Column(String, nullable=True)

    source_url = Column(String, nullable=True)
    source_last_updated = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    progress = relationship("WorkProgress", back_populates="work", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="work", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="work", cascade="all, delete-orphan")


class WorkProgress(Base):
    __tablename__ = "work_progress"

    progress_id = Column(String, primary_key=True, index=True)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    recorded_at = Column(DateTime, nullable=True)
    physical_progress_pct = Column(Float, nullable=True)
    financial_progress_pct = Column(Float, nullable=True)
    cumulative_payment = Column(Float, nullable=True)
    payment_since_previous_update = Column(Float, nullable=True)
    status_at_update = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
    data_source = Column(String, nullable=True)

    work = relationship("Work", back_populates="progress")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(String, primary_key=True, index=True)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    contractor_name = Column(String, nullable=True)
    request_date = Column(DateTime, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    payment_date = Column(DateTime, nullable=True)
    amount = Column(Float, nullable=True)
    payment_stage = Column(String, nullable=True)
    payment_status = Column(String, nullable=True)
    data_source = Column(String, nullable=True)

    work = relationship("Work", back_populates="payments")


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(String, primary_key=True, index=True)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    mp_name = Column(String, nullable=True)
    recommendation_date = Column(DateTime, nullable=True)
    recommended_amount = Column(Float, nullable=True)
    recommended_sector = Column(String, nullable=True)
    recommendation_status = Column(String, nullable=True)
    data_source = Column(String, nullable=True)

    work = relationship("Work", back_populates="recommendations")


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    issue_id = Column(String, primary_key=True, index=True)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    field = Column(String, nullable=True)
    issue_type = Column(String, nullable=False)
    severity = Column(String, nullable=True)
    observed_value = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    data_source = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class GuidelineRule(Base):
    __tablename__ = "guideline_rules"

    rule_id = Column(String, primary_key=True, index=True)
    rule_name = Column(String, nullable=False)
    rule_description = Column(Text, nullable=True)
    source_document = Column(String, nullable=True)
    source_version = Column(String, nullable=True)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    scope = Column(String, nullable=True)
    calculation_method = Column(String, nullable=True)
    threshold = Column(Float, nullable=True)
    severity = Column(String, nullable=True)
    advisory_or_mandatory = Column(String, default="advisory")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class DetectorEvidence(Base):
    __tablename__ = "detector_evidence"

    evidence_id = Column(String, primary_key=True, index=True)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    detector_id = Column(String, nullable=False)
    rule_id = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    metric_name = Column(String, nullable=True)
    observed_value = Column(String, nullable=True)
    reference_value = Column(String, nullable=True)
    difference = Column(String, nullable=True)
    percentage_difference = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    source_fields = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    assessment_id = Column(String, primary_key=True, index=True)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    score_decomposition = Column(String, nullable=True)
    detector_contributions = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ReconciliationConflict(Base):
    """Cross-source reconciliation conflict (Section 12 of upgrade spec)."""
    __tablename__ = "reconciliation_conflicts"

    conflict_id = Column(String, primary_key=True, index=True)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    field = Column(String, nullable=True)
    source_a = Column(String, nullable=True)
    value_a = Column(String, nullable=True)
    source_b = Column(String, nullable=True)
    value_b = Column(String, nullable=True)
    conflict_type = Column(String, nullable=False, default="RECONCILIATION_CONFLICT")
    reason = Column(Text, nullable=True)
    severity = Column(String, nullable=True)
    evidence_quality = Column(String, nullable=True)
    review_status = Column(String, nullable=False, default="OPEN")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class ReviewPriorityLog(Base):
    """Phase 15 — Review priority log (evidence-first, not fraud probability)."""
    __tablename__ = "review_priority_logs"

    log_id = Column(String, primary_key=True, index=True)
    work_id = Column(String, ForeignKey("works.work_id"), nullable=False, index=True)
    review_priority = Column(String, nullable=False)
    evidence_quality = Column(String, nullable=True)
    score = Column(Float, nullable=True)
    num_independent_signals = Column(Integer, nullable=True)
    component_reasons_json = Column(JSON, nullable=True)
    detector_contributions_json = Column(JSON, nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class SourceRun(Base):
    __tablename__ = "source_runs"

    run_id = Column(String, primary_key=True, index=True)
    source_name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    retrieved_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    source_last_updated = Column(DateTime, nullable=True)
    dataset_version = Column(String, nullable=True)
    record_count = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="COMPLETED")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
