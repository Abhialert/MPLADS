"""Timeline Analysis Detector — PARTIALLY_EVALUABLE (observed duration only)."""
from typing import List, Optional, Dict, Any
from datetime import datetime

class TimelineAnomalyDetector:
    name = "TIMELINE"
    description = "Observed duration analysis (not full timeline anomaly)."
    required_fields = ["work_id","recommendation_date","sanction_date","actual_completion_date"]
    missing_for_guideline = ["expected_completion_date","ia_assignment_date"]

    def analyze(self, work: Dict[str, Any]) -> Dict[str, Any]:
        wid = work.get("work_id","UNKNOWN")
        rec = work.get("recommendation_date")
        sanc = work.get("sanction_date")
        comp = work.get("actual_completion_date")
        if not all(isinstance(x, datetime) for x in [rec, sanc, comp] if x):
            return {"detector_id":self.name,"mode":"NOT_EVALUABLE","reason":"Missing/invalid dates","guideline_compliance_evaluated":False,"limitations":"Only observed durations computed; expected_completion_date unavailable for guideline comparison."}
        if isinstance(rec, datetime) and isinstance(sanc, datetime) and isinstance(comp, datetime):
            r2s = (sanc-rec).days
            s2c = (comp-sanc).days
            r2c = (comp-rec).days
            flags = []
            if r2s < 0: flags.append({"type":"SANCTION_BEFORE_RECOMMENDATION","days":r2s})
            if s2c < 0: flags.append({"type":"COMPLETION_BEFORE_SANCTION","days":s2c})
            return {"detector_id":self.name,"work_id":wid,"mode":"OBSERVED_DURATION_ANALYSIS","label":"OBSERVED_DURATION_ANALYSIS",
                    "observed_duration_days":{"recommendation_to_sanction":r2s,"sanction_to_completion":s2c,"recommendation_to_completion":r2c},
                    "guideline_compliance_evaluated":False,"reason_guideline_not_evaluated":"expected_completion_date unavailable from public source",
                    "flags":flags,"limitations":"No statistical baseline or guideline comparison performed.","source_fields":["recommendation_date","sanction_date","actual_completion_date"],
                    "observed_at":datetime.utcnow().isoformat(),"real_data_capability_note":"REAL_ESAKSHI: full observed duration; SYNTHETIC: can include expected_completion_date."}
        return {"detector_id":self.name,"mode":"NOT_EVALUABLE","reason":"Dates missing"}

    def batch_analyze(self, works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.analyze(w) for w in works]

    def get_coverage(self) -> Dict[str, Any]:
        return {"detector_id":self.name,"capability":"PARTIALLY_EVALUABLE","real_mode_label":"OBSERVED_DURATION_ANALYSIS","required_fields":self.required_fields,"available_fields":self.required_fields,"missing_for_guideline":["expected_completion_date","ia_assignment_date","final_payment_date","marked_complete_date"],"note":"Only observed durations computed; guideline comparison requires unavailable fields."}

    def get_evidence_template(self) -> Dict[str, Any]:
        return {"detector_id":self.name,"metric_name":"observed_duration_days","observed_value":None,"reference_value":None,"difference":None,"percentage_difference":None,"unit":"days","source_fields":["recommendation_date","sanction_date","actual_completion_date"],"explanation":"Days between available dates; not compared against official guideline expectation."}
