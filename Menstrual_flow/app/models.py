from pydantic import BaseModel
from datetime import datetime
from typing import List

########## Input for single reading ##########
class Reading(BaseModel):
    timestamp: datetime
    flow_ml: float
    user_email: str

########## Input for batch(multiple) readings ##########
class BatchReadings(BaseModel):
    readings: List[Reading]
