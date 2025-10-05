from typing import List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from app.storage.memory_store import cycles_db, next_cycle_id
from app.services.data_service import list_all_readings
# A new cycle starts on any day where flow_ml > 0 and the previous day had flow_ml == 0
# Cycle ends the day before the next start. Single-day cycles allowed.
# If data starts mid-cycle (i.e., first day has flow > 0 and we don't know prev day),
# we still consider that the start of a cycle.

def rebuild_cycles_for_user(user_email: str) -> List[Dict[str, Any]]:
    daily = _collapse_to_daily(list_all_readings(user_email))      # collect daily readings (reccomended - one per day; if multiple, sum and avg it)

    if not daily:
        _purge_user_cycles(user_email)
        return []

    starts = _detect_cycle_starts(daily)

    spans: List[Tuple[date, date]] = []
    for i, start_idx in enumerate(starts):
        start_day = daily[start_idx]["day"]
        if i + 1 < len(starts):
            next_start_day = daily[starts[i + 1]]["day"]
            end_day = next_start_day - timedelta(days=1)
        else:
            end_day = daily[-1]["day"]
        if end_day < start_day:
            end_day = start_day
        spans.append((start_day, end_day))


######### existing cycles (history) #########
    _purge_user_cycles(user_email)
    for s, e in spans:
        cycles_db.append({
            "id": next_cycle_id(),
            "user_email": user_email,
            "start_date": s,
            "end_date": e,
        })

    return list_cycles_for_user(user_email)

def list_cycles_for_user(user_email: str) -> List[Dict[str, Any]]:
    return sorted(
        [c for c in cycles_db if c["user_email"] == user_email],
        key=lambda x: x["start_date"],
    )

def get_cycle_by_id(user_email: str, cycle_id: int) -> Dict[str, Any] | None:
    for c in cycles_db:
        if c["user_email"] == user_email and c["id"] == cycle_id:
            return c
    return None

def compute_cycle_summary(user_email: str, cycle_id: int) -> Dict[str, Any]:
    cycle = get_cycle_by_id(user_email, cycle_id)
    if not cycle:
        return {}

    start: date = cycle["start_date"]
    end: date = cycle["end_date"]
    rows = _collapse_to_daily(list_all_readings(user_email))
    window = [r for r in rows if start <= r["day"] <= end]
    if not window:
        return {
            "cycle_id": cycle_id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "days": 0,
            "total_flow_ml": 0,
            "avg_daily_ml": 0,
            "peak_ml": 0,
            "peak_day": None,
        }

    total = sum(r["flow_ml"] for r in window)
    days = (end - start).days + 1
    peak = max(window, key=lambda x: x["flow_ml"])
    return {
        "cycle_id": cycle_id,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "days": days,
        "total_flow_ml": total,
        "avg_daily_ml": round(total / days, 2),
        "peak_ml": peak["flow_ml"],
        "peak_day": peak["day"].isoformat(),
    }

def overall_flow_summary(user_email: str) -> Dict[str, Any]:
    rows = _collapse_to_daily(list_all_readings(user_email))
    if not rows:
        return {"user_email": user_email, "cycles": 0, "avg_cycle_length_days": None, "avg_total_flow_ml": None}

    cycles = list_cycles_for_user(user_email)
    if not cycles:
        return {"user_email": user_email, "cycles": 0, "avg_cycle_length_days": None, "avg_total_flow_ml": None}

    lens = []
    totals = []
    for c in cycles:
        start, end = c["start_date"], c["end_date"]
        window = [r for r in rows if start <= r["day"] <= end]
        if not window:
            continue
        lens.append((end - start).days + 1)
        totals.append(sum(r["flow_ml"] for r in window))

    return {
        "user_email": user_email,
        "cycles": len(cycles),
        "avg_cycle_length_days": round(sum(lens)/len(lens), 1) if lens else None,
        "avg_total_flow_ml": round(sum(totals)/len(totals), 1) if totals else None,
    }

    ###### Remove existing cycles of this user (in place) ########
def _purge_user_cycles(user_email: str) -> None:
    to_keep = [c for c in cycles_db if c["user_email"] != user_email]
    cycles_db.clear()
    cycles_db.extend(to_keep)

def _collapse_to_daily(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group readings by day; if multiple same-day readings exist, sum flow."""
    by_day: Dict[date, int] = {}
    for r in rows:
        ts = r["timestamp"]
        if isinstance(ts, str):
            dt = datetime.fromisoformat(ts)
        else:
            dt = ts
        d = dt.date()
        by_day[d] = by_day.get(d, 0) + int(r.get("flow_ml", 0))
    out = [{"day": d, "flow_ml": ml} for d, ml in by_day.items()]
    return sorted(out, key=lambda x: x["day"])

def _detect_cycle_starts(daily: List[Dict[str, Any]]) -> List[int]:
    starts: List[int] = []
    for i, row in enumerate(daily):
        ml = row["flow_ml"]
        prev_ml = daily[i-1]["flow_ml"] if i > 0 else 0
        if ml > 0 and prev_ml == 0:
            starts.append(i)
    if not starts and daily and daily[0]["flow_ml"] > 0:
        starts.append(0)          ####### fallback: first day is a start #####
    return starts
