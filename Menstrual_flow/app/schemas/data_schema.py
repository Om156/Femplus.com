from pydantic import BaseModel
from typing import Optional

class FlowData(BaseModel):
    flow_ml: float
    hb: float
    ph: float
    crp: float
    hba1c_ratio: float
    clots_score: float
    fsh_level: float
    lh_level: float
    amh_level: float
    tsh_level: float
    prolactin_level: float
    
    # Additional parameters for comprehensive menstrual health diagnosis
    esr: Optional[float] = None  # Erythrocyte Sedimentation Rate
    leukocyte_count: Optional[float] = None  # White Blood Cell count
    vaginal_ph: Optional[float] = None  # Vaginal pH (separate from general pH)
    ca125: Optional[float] = None  # CA-125 tumor marker
    estrogen: Optional[float] = None  # Estradiol/E2
    progesterone: Optional[float] = None  # Progesterone levels
    androgens: Optional[float] = None  # Testosterone levels
    blood_glucose: Optional[float] = None  # Fasting blood glucose
    wbc_count: Optional[float] = None  # White Blood Cell count (alternative)
    
    # Disease-specific symptom tracking
    pain_score: Optional[float] = None  # Pain intensity (0-10)
    weight_gain: Optional[float] = None  # Weight change in kg
    acne_severity: Optional[float] = None  # Acne severity score (0-5)
    insulin_resistance: Optional[float] = None  # HOMA-IR score
    fever: Optional[float] = None  # Temperature in Celsius
    tenderness: Optional[int] = None  # Tenderness score (0-3)
    pain_during_intercourse: Optional[int] = None  # 0/1 boolean
    bloating: Optional[int] = None  # 0/1 boolean
    weight_loss: Optional[float] = None  # Weight loss in kg
    appetite_loss: Optional[int] = None  # 0/1 boolean
    vaginal_discharge: Optional[str] = None  # Description of discharge
    discharge_odor: Optional[str] = None  # Odor description
    discharge_color: Optional[str] = None  # Color description

class DiseaseSpecificData(BaseModel):
    """Model for disease-specific parameter collection"""
    disease_type: str  # PCOS, PID, Endometriosis, Cancer
    parameters: dict  # Dynamic parameters based on disease type
    manual_input: Optional[dict] = None  # Manual entry data
    device_data: Optional[dict] = None  # Device sensor data
    image_data: Optional[str] = None  # Base64 encoded image
