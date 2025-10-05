from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.ml.ml_service import predict_flow_risk, save_user_entry

router = APIRouter(
    tags=["ML"]
)

class FlowInput(BaseModel):
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
    image_base64: Optional[str] = None
    label: Optional[str] = None
    esr:Optional[float] = None
    leukocyte_count: Optional[float] = None
    vaginal_ph: Optional[float] = None
    ca125: Optional[float] = None
    estrogen: Optional[float] = None
    progesterone: Optional[float] = None
    androgens: Optional[float] = None
    blood_glucose: Optional[float] = None
    wbc_count: Optional[float] = None
    pain_score: Optional[float] = None
    weight_gain: Optional[float] = None
    acne_severity: float = None
    insulin_resistance: Optional[float] = None
    fever: Optional[float]   = None
    tenderness: Optional[float] = None
    pain_during_intercourse: Optional[float] = None
    bloating: Optional[float] = None
    weight_loss: Optional[float] = None
    appetite_loss: Optional[float] = None
    vaginal_discharge: Optional[float] = None
    discharge_odor: Optional[float]  = None
    discharge_color: Optional[float] = None

@router.post("/predict")
async def predict_flow(input_data: FlowInput):
    try:
        features = input_data.dict()
        label = features.pop("label", None)
        image_base64 = features.pop("image_base64", None)

        if label is not None:
            save_user_entry(features, label)

        result = predict_flow_risk(features, image_base64=image_base64)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


# Alias path to satisfy frontend calling /flow/predict
@router.post("/flow/predict")
async def predict_flow_alias(input_data: FlowInput):
    return await predict_flow(input_data)