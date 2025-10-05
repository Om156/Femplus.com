from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal
from datetime import date

FlowLevel = Literal["none", "light", "medium", "heavy"]

class CycleStartIn(BaseModel):
    user_email: EmailStr
    start_date: Optional[date] = None
    notes: Optional[str] = None

class FlowLogIn(BaseModel):
    user_email: EmailStr
    cycle_id: str
    date: Optional[date] = None
    flow_level: FlowLevel = "none"
    flow_ml: Optional[float] = None
    pads_used: Optional[int] = None
    pain_level: Optional[int] = Field(None, ge=0, le=10, description="0-10 pain scale")
    mood: Optional[str] = None
    symptoms: Optional[List[str]] = []

class CycleEndIn(BaseModel):
    user_email: EmailStr
    cycle_id: str
    end_date: Optional[date] = None
    notes: Optional[str] = None

class CycleOut(BaseModel):
    cycle_id: str
    user_email: EmailStr
    start_date: date
    end_date: Optional[date] = None
    notes: Optional[str]
    closed: bool

class FlowLogOut(FlowLogIn):
    log_id: int
