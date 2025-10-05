from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any
from app.services.cycle_service import (
    rebuild_cycles_for_user,
    list_cycles_for_user,
    compute_cycle_summary,
    overall_flow_summary,
)

router = APIRouter(prefix="/flow", tags=["flow"])

@router.post("/rebuild", summary="Rebuild cycles for a user from stored flow readings")
def rebuild(user_email: str = Query(..., example="user@example.com")) -> Dict[str, Any]:
    cycles = rebuild_cycles_for_user(user_email)
    return {"user_email": user_email, "cycles_built": len(cycles), "cycles": [
        {
            "id": c["id"],
            "start_date": c["start_date"].isoformat(),
            "end_date": c["end_date"].isoformat(),
        } for c in cycles
    ]}

@router.get("/cycles", summary="List detected cycles for a user")
def list_cycles(user_email: str = Query(..., example="user@example.com")) -> Dict[str, Any]:
    cycles = list_cycles_for_user(user_email)
    return {"user_email": user_email, "cycles": [
        {
            "id": c["id"],
            "start_date": c["start_date"].isoformat(),
            "end_date": c["end_date"].isoformat(),
        } for c in cycles
    ]}

@router.get("/cycles/{cycle_id}/summary", summary="Summary for one cycle")
def cycle_summary(cycle_id: int, user_email: str = Query(..., example="user@example.com")) -> Dict[str, Any]:
    summary = compute_cycle_summary(user_email, cycle_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return summary

@router.get("/summary", summary="Overall flow summary for a user")
def overall_summary(user_email: str = Query(..., example="user@example.com")) -> Dict[str, Any]:
    return overall_flow_summary(user_email)
