from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.storage.model import Feedback


router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackIn(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    context_type: Optional[str] = None  # home, feature, labs, shop, analysis
    context_id: Optional[str] = None
    user_email: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    context_type: Optional[str]
    context_id: Optional[str]
    user_email: Optional[str]

    class Config:
        orm_mode = True


@router.post("/", response_model=FeedbackOut, status_code=201)
def create_feedback(payload: FeedbackIn, db: Session = Depends(get_db)):
    fb = Feedback(
        rating=int(payload.rating),
        comment=(payload.comment or '')[:1000] if payload.comment else None,
        context_type=(payload.context_type or None),
        context_id=(payload.context_id or None),
        user_email=(payload.user_email or None),
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb


@router.get("/public", response_model=List[FeedbackOut])
def list_public_feedback(limit: int = 12, db: Session = Depends(get_db)):
    q = db.query(Feedback).order_by(Feedback.created_at.desc()).limit(max(1, min(limit, 50)))
    return q.all()


@router.get("/summary")
def feedback_summary(db: Session = Depends(get_db)):
    rows = db.query(Feedback.rating).all()
    ratings = [r[0] for r in rows if isinstance(r[0], int)]
    if not ratings:
        return {"count": 0, "avg": None}
    avg = round(sum(ratings)/len(ratings), 2)
    return {"count": len(ratings), "avg": avg}


