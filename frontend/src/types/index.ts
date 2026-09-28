export interface Work {
  work_id: string;
  source_work_id?: string | null;
  data_source?: string | null;
  mp_name: string | null;
  mp_type?: string | null;
  constituency: string | null;
  state: string | null;
  district: string | null;
  financial_year: string | null;
  sector?: string | null;
  work_description: string | null;
  implementing_agency: string | null;
  contractor_name: string | null;
  location_text: string | null;
  latitude: number | null;
  longitude: number | null;
  is_within_constituency: boolean | null;
  is_sc_area: boolean | null;
  is_st_area: boolean | null;
  beneficiary_type: string | null;
  asset_owner_type: string | null;
  recommended_amount: number | null;
  sanctioned_amount: number | null;
  actual_expenditure: number | null;
  total_paid: number | null;
  recommendation_date: string | null;
  sanction_date: string | null;
  ia_assignment_date: string | null;
  expected_completion_date: string | null;
  actual_completion_date: string | null;
  final_payment_date: string | null;
  marked_complete_date: string | null;
  status: string | null;
  source_url: string | null;
  source_last_updated: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface SystemStatus {
  db: string;
  db_status: string;
  total_works: number;
  mode: string;
  evidence_pipeline: string;
  detectors: string[];
  note: string;
}

export interface DetectorCoverage {
  [detectorName: string]: boolean | any;
  metadata?: {
    total_records_evaluated: number;
    provenance_standard: string;
    last_audit_run: string;
  };
}
