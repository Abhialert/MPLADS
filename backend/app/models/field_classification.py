"""Explicit classification of every work field by observation status."""

FIELD_CLASSIFICATION = {
    # OBSERVED: present in public MPLADS export
    "work_id": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "work_id"},
    "mp_name": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "mp_name"},
    "state": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "state"},
    "constituency": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "constituency"},
    "work_description": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "work_description"},
    "financial_year": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "financial_year"},
    "recommended_amount": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "recommended_amount"},
    "sanctioned_amount": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "sanctioned_amount"},
    "actual_expenditure": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "actual_expenditure"},
    "status": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "status"},
    "recommendation_date": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "recommendation_date"},
    "sanction_date": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "sanction_date"},
    "actual_completion_date": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "actual_completion_date"},
    "location_text": {"status": "observed", "source": "mplads_dashboard_export", "provenance_key": "location_text"},

    # UNAVAILABLE: not in public export (verified by adapter.get_source_coverage() False)
    "expected_completion_date": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Not provided by public source; required for full timeline guideline evaluation"},
    "district": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Requires additional geographic/district data source"},
    "latitude": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Requires geocoding or separate GIS source"},
    "longitude": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Requires geocoding or separate GIS source"},
    "is_within_constituency": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Requires constituency boundary GIS layer + point-in-polygon"},
    "is_sc_area": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Requires official SC/ST area designation data"},
    "is_st_area": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Requires official SC/ST area designation data"},
    "contractor_name": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Not in public export; needed for vendor/pattern analysis"},
    "total_paid": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Not in public export; limits expenditure completeness"},
    "final_payment_date": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Not in public export; needed for full timeline/pay analysis"},
    "sector": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Not consistently available in public export"},
    "beneficiary_type": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Not in public export"},
    "asset_owner_type": {"status": "unavailable", "source": "mplads_dashboard_export", "note": "Not in public export"},

    # DERIVED: computed by detectors (not from raw source)
    "execution_percentage": {"status": "derived", "source": "detector_cost_anomaly", "calculation": "actual_expenditure / sanctioned_amount * 100"},
    "observed_duration_days": {"status": "derived", "source": "detector_timeline", "calculation": "date arithmetic on recommendation/sanction/completion"},
    "risk_score": {"status": "derived", "source": "detector_ensemble", "note": "Composite; requires detector outputs as inputs; no single public source"},

    # SECONDARY SOURCE (potential future integration)
    "vendor_concentration": {"status": "secondary_source", "source": "esakshi_payment_export_or_contract_reg", "note": "Requires separate data integration"},
    "geographic_compliance": {"status": "secondary_source", "source": "gis_boundary_layer", "note": "Requires GIS source for constituency boundary verification"},
}
