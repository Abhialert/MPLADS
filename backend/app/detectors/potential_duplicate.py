"""Potential Duplicate Detector for MPLAD Integrity Engine.

Uses work description similarity, location text similarity, constituency,
state, and date proximity to identify pairs that may represent the
same or highly similar works.

Does NOT require geographic coordinates. Uses text-based assessment.
"""

import re
from collections import Counter
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime


class PotentialDuplicateDetector:
    """Duplicate/Potential Duplicate Assessment Detector."""

    def __init__(self):
        self.name = "DUPLICATE"
        self.description = "Potential duplicate assessment using text, entity, and temporal evidence"
        self.required_fields = ["work_id", "work_description", "location_text",
                                "constituency", "state", "recommendation_date"]
        self.available_fields = ["work_id", "work_description", "location_text",
                                 "constituency", "state", "recommendation_date",
                                 "sanction_date", "actual_completion_date",
                                 "sanctioned_amount", "actual_expenditure"]
        self.missing_fields = [f for f in self.required_fields if f not in self.available_fields]

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for comparison."""
        if not text or not isinstance(text, str):
            return []
        # Lowercase, split on whitespace/punctuation
        return re.findall(r'\b\w+\b', text.lower())

    def _jaccard_similarity(self, set_a: set, set_b: set) -> float:
        """Compute Jaccard similarity between two sets."""
        if not set_a and not set_b:
            return 0.0
        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def _compute_description_similarity(self, desc_a: str, desc_b: str) -> float:
        """
        Compute description similarity using token-based (Jaccard) similarity.

        Uses Jaccard similarity on word tokens as a transparent,
        explainable method.
        """
        if not desc_a or not desc_b:
            return 0.0
        tokens_a = set(self._tokenize(desc_a))
        tokens_b = set(self._tokenize(desc_b))
        return self._jaccard_similarity(tokens_a, tokens_b)

    def _compute_location_similarity(self, loc_a: str, loc_b: str) -> float:
        """
        Compute location text similarity.

        Uses Jaccard similarity on character n-grams (3-grams)
        for robust comparison of location text.
        """
        if not loc_a or not loc_b:
            return 0.0
        # Use character trigrams
        def trigrams(text: str) -> set:
            text = text.lower().strip()
            return set(text[i:i+3] for i in range(len(text) - 2))

        trig_a = trigrams(loc_a)
        trig_b = trigrams(loc_b)
        return self._jaccard_similarity(trig_a, trig_b)

    def _date_proximity(self, date_a: datetime, date_b: datetime) -> Optional[int]:
        """Return number of days between two dates, or None if either is missing."""
        if not date_a or not date_b:
            return None
        delta = abs((date_a - date_b).days)
        return delta

    def _analyze_pair(self, work_a: Dict[str, Any], work_b: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a pair of works for similarity."""
        work_id_a = work_a.get("work_id")
        work_id_b = work_b.get("work_id")

        # Description similarity (Jaccard on word tokens)
        desc_sim = self._compute_description_similarity(
            work_a.get("work_description"), work_b.get("work_description")
        )

        # Location similarity (Jaccard on char trigrams)
        loc_sim = self._compute_location_similarity(
            work_a.get("location_text"), work_b.get("location_text")
        )

        # Entity matching
        constituency_match = (work_a.get("constituency") and work_b.get("constituency")
                              and work_a["constituency"].strip().lower() == work_b["constituency"].strip().lower())
        state_match = (work_a.get("state") and work_b.get("state")
                       and work_a["state"].strip().lower() == work_b["state"].strip().lower())

        # Date proximity
        rec_a = work_a.get("recommendation_date")
        rec_b = work_b.get("recommendation_date")
        date_proximity = self._date_proximity(rec_a, rec_b) if rec_a and rec_b else None

        # Calculate composite similarity score (weighted average)
        score = 0.0
        weights = {"description": 0.4, "location": 0.3, "constituency": 0.2, "date": 0.1}
        count = 0.0

        if desc_sim > 0:
            score += weights["description"] * desc_sim
            count += weights["description"]
        if loc_sim > 0:
            score += weights["location"] * loc_sim
            count += weights["location"]
        if constituency_match:
            score += weights["constituency"] * 1.0
            count += weights["constituency"]
        if state_match:
            score += weights["state"] * 1.0
            count += weights["state"]
        if date_proximity is not None and date_proximity <= 90:
            score += weights["date"] * max(0, 1 - (date_proximity / 90))
            count += weights["date"]

        final_score = round(score / count, 4) if count > 0 else 0.0

        # Threshold for flagging
        THRESHOLD = 0.6

        if final_score < THRESHOLD:
            return None

        # Build evidence
        explanation_parts = []
        if desc_sim > 0.5:
            explanation_parts.append(f"Work description similarity: {desc_sim*100:.1f}%")
        if loc_sim > 0.3:
            explanation_parts.append(f"Location text similarity: {loc_sim*100:.1f}%")
        if constituency_match:
            explanation_parts.append(f"Constituency match: Yes ({work_a.get('constituency')})")
        if state_match:
            explanation_parts.append(f"State match: Yes ({work_a.get('state')})")
        if date_proximity is not None and date_proximity <= 90:
            explanation_parts.append(f"Date overlap (recommendation): {date_proximity} days")

        # Classification
        level = "POTENTIAL_DUPLICATE"
        if final_score >= 0.8:
            level = "HIGH_SIMILARITY"

        return {
            "detector_id": self.name,
            "work_a": work_id_a,
            "work_b": work_id_b,
            "classification": level,
            "similarity_score": final_score,
            "threshold": THRESHOLD,
            "description_similarity_pct": round(desc_sim * 100, 2),
            "location_similarity_pct": round(loc_sim * 100, 2),
            "constituency_match": constituency_match,
            "state_match": state_match,
            "date_overlap_days": date_proximity,
            "explanation": "; ".join(explanation_parts) if explanation_parts else "Multiple similarity indicators suggest potential duplicate.",
            "source_fields": [
                "work_description", "location_text",
                "constituency", "state", "recommendation_date"
            ],
            "limitations": (
                "Geographic distance unavailable (coordinates not provided). "
                "Similarity based on location text and entity matching only. "
                "This is a POTENTIAL duplicate assessment, not confirmed duplication."
            ),
            "observed_at": datetime.utcnow().isoformat()
        }

    def analyze(self, work: Dict[str, Any], all_works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze a work against all others for potential duplicates.

        Args:
            work: The target work record
            all_works: All work records to compare against

        Returns:
            List of potential duplicate pairs
        """
        results = []
        for other in all_works:
            if other.get("work_id") == work.get("work_id"):
                continue
            pair_result = self._analyze_pair(work, other)
            if pair_result is not None:
                results.append(pair_result)
        return results

    def batch_analyze(self, works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze all works for potential duplicates (pairwise).

        Args:
            works: List of work records

        Returns:
            List of potential duplicate pair assessments
        """
        results = []
        for i, work in enumerate(works):
            pairs = self.analyze(work, works)
            results.extend(pairs)
        # Deduplicate (only keep each pair once)
        seen = set()
        unique = []
        for r in results:
            key = tuple(sorted([r["work_a"], r["work_b"]]))
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    def get_coverage(self) -> Dict[str, Any]:
        """Return detector coverage information."""
        return {
            "detector_id": self.name,
            "fully_evaluable": True,
            "partially_evaluable": False,
            "not_evaluable": False,
            "required_fields": self.required_fields,
            "available_fields": self.available_fields,
            "missing_fields": self.missing_fields,
            "safe_real_output": (
                "POTENTIAL_DUPLICATE assessment using description similarity, "
                "location text similarity, constituency match, state match, "
                "and date proximity. No geographic distance calculation (coordinates unavailable)."
            ),
            "limitations": (
                "Geographic distance unavailable (no coordinates in source). "
                "Similarity based on text and entity matching only. "
                "Results are screening indicators, not confirmed duplicates."
            ),
            "real_data_label": "POTENTIAL_DUPLICATE"
        }

    def get_evidence_template(self) -> Dict[str, Any]:
        """Return evidence template for this detector."""
        return {
            "detector_id": self.name,
            "metric_name": "similarity_score",
            "observed_value": None,
            "reference_value": 0.6,
            "difference": None,
            "percentage_difference": None,
            "unit": "score",
            "source_fields": ["work_description", "location_text",
                             "constituency", "state", "recommendation_date"],
            "explanation": "Composite similarity score from description, location, "
                          "constituency, and date proximity components."
        }