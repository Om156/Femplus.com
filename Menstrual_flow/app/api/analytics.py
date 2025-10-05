from typing import Dict, Any, List
from collections import defaultdict
from app.services.data_service import list_all_readings

def _sum_flow_by_cycle(readings: List) -> Dict[str, float]:
    cycle_totals = defaultdict(float)
    for r in readings:
        if r.flow_ml is not None:
            cycle_id = getattr(r, "cycle_id", "unknown")
            cycle_totals[cycle_id] += float(r.flow_ml)
    return dict(cycle_totals)

def compute_summary(user_email: str) -> Dict[str, Any]:
    readings = list_all_readings(user_email)
    if not readings:
        return {"user_email": user_email, "message": "No readings found", "flags": {}}

    latest = max(readings, key=lambda r: r.timestamp)

    cycle_totals = _sum_flow_by_cycle(readings)
    flags = {}

    # Anemia
    if latest.hb is not None:
        flags["anemia_risk"] = "high" if latest.hb < 12.0 else "low"

    # Vaginal infection risk (pH > 4.5)
    if latest.ph is not None:
        flags["ph_alert"] = "high" if latest.ph > 4.5 else "low"

    # Inflammation (CRP > 10 mg/L)
    if latest.crp is not None:
        flags["inflammation"] = "high" if latest.crp > 10 else "low"

    # Diabetes detection from HbA1c
    if latest.hba1c_ratio is not None:
        if latest.hba1c_ratio >= 6.5:
            flags["diabetes_flag"] = "high"
        elif 5.7 <= latest.hba1c_ratio < 6.5:
            flags["diabetes_flag"] = "moderate"
        else:
            flags["diabetes_flag"] = "low"

    # Clots
    if latest.clots_score is not None:
        flags["clots_alert"] = "high" if latest.clots_score >= 2 else "low"

    # Menorrhagia (>80 ml per cycle)
    menorrhagia_cycles = {cid: vol for cid, vol in cycle_totals.items() if vol > 80.0}
    flags["menorrhagia_cycles"] = list(menorrhagia_cycles.keys())

    return {
        "user_email": user_email,
        "latest": {
            "timestamp": latest.timestamp,
            "flow_ml": latest.flow_ml,
            "hb": latest.hb,
            "ph": latest.ph,
            "crp": latest.crp,
            "hba1c_ratio": latest.hba1c_ratio,
            "clots_score": latest.clots_score,
        },
        "cycle_flow_totals_ml": cycle_totals,
        "flags": flags
    }
