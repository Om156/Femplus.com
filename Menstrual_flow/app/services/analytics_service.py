from typing import Dict, Any, List
from collections import defaultdict
from app.services.data_service import list_all_readings

def _sum_flow_by_cycle(readings: list) -> dict:
    totals = defaultdict(float)
    for r in readings:
        flow = r.get("flow_ml")
        if flow is not None:
            cycle_id = r.get("cycle_id") or "unknown"
            totals[cycle_id] += float(flow)
    return dict(totals)

def _get_latest_metric(readings: list, field: str):
    filtered = [r for r in readings if r.get(field) is not None]
    if not filtered:
        return None
    return filtered[-1][field]


def compute_summary(user_email: str) -> Dict[str, Any]:
    readings = list_all_readings(user_email)

    # Pull latest values for each metric
    hb = _get_latest_metric(readings, "hb")
    ph = _get_latest_metric(readings, "ph")
    le = _get_latest_metric(readings, "le")
    crp = _get_latest_metric(readings, "crp")
    hba1c = _get_latest_metric(readings, "hba1c_ratio")
    clots = _get_latest_metric(readings, "clots_score")
    flow_ml = _get_latest_metric(readings, "flow_ml")


    flags = {}

    if hb is not None:
        flags["anemia_risk"] = "high" if hb < 12.0 else "low"
    if ph is not None:
        flags["ph_alert"] = "high" if ph > 4.5 else "low"
    if crp is not None:
        flags["inflammation"] = "high" if crp > 10 else "low"
    if hba1c is not None:
        if hba1c >= 6.5:
            flags["diabetes_flag"] = "high"
        elif 5.7 <= hba1c < 6.5:
            flags["diabetes_flag"] = "moderate"
        else:
            flags["diabetes_flag"] = "low"
    if clots is not None:
        flags["clots_alert"] = "high" if clots >= 2 else "low"

    cycle_totals = _sum_flow_by_cycle(readings)
    menorrhagia_cycles = {cid: vol for cid, vol in cycle_totals.items() if vol > 80.0}
    flags["menorrhagia_cycles"] = list(menorrhagia_cycles.keys())

    latest = {
        "hb": hb,
        "ph": ph,
        "crp": crp,
        "hba1c_ratio": hba1c,
        "clots_score": clots,
        "flow_ml": flow_ml
    }

    return {
        "user_email": user_email,
        "latest": latest,
        "cycle_flow_totals_ml": cycle_totals,
        "flags": flags
    }
