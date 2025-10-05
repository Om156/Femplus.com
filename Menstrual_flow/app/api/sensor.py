from fastapi import APIRouter
from app.api.ml import FlowInput
from app.ml.ml_service import predict_flow_risk, save_user_entry, retrain_model_incremental

router = APIRouter()

@router.post("/sensor_feed")
def sensor_feed(sensor_data: FlowInput):
    features = sensor_data.dict()
    image = features.pop("image_base64", None)
    result = predict_flow_risk(features, image_base64=image)
    save_user_entry(features, label=result['prediction'])
    retrain_model_incremental()
    return result
