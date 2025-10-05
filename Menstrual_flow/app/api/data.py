from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services import data_service
from app.services.thingspeak_service import thingspeak_service

router = APIRouter()

class SingleReadingInput(BaseModel):
    user_email: str
    flow_ml: float = 0.0
    hb: float = None
    ph: float = None
    crp: float = None
    hba1c_ratio: float = None
    clots_score: float = None
    cycle_id: str = "unknown"
    fsh_level: Optional[float] = None
    lh_level: Optional[float] = None
    amh_level: Optional[float] = None
    tsh_level: Optional[float] = None
    prolactin_level: Optional[float] = None
    # Gas sensor data
    co2_ppm: Optional[float] = None
    co_ppm: Optional[float] = None
    no2_ppb: Optional[float] = None
    o3_ppb: Optional[float] = None
    pm25_ugm3: Optional[float] = None
    pm10_ugm3: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    air_quality_index: Optional[float] = None
    air_quality_category: Optional[str] = None
    # TCS230 Color sensor data
    color_red: Optional[float] = None
    color_green: Optional[float] = None
    color_blue: Optional[float] = None
    color_clear: Optional[float] = None
    color_hue: Optional[float] = None
    color_saturation: Optional[float] = None
    color_brightness: Optional[float] = None
    color_temperature: Optional[float] = None
    color_category: Optional[str] = None

@router.post("/single")
def add_single_reading(input: SingleReadingInput):
    return data_service.add_single_reading(
        user_email=input.user_email,
        flow_ml=input.flow_ml,
        hb=input.hb,
        ph=input.ph,
        crp=input.crp,
        hba1c_ratio=input.hba1c_ratio,
        clots_score=input.clots_score,
        fsh_level=input.fsh_level,
        lh_level=input.lh_level,
        amh_level=input.amh_level,
        tsh_level=input.tsh_level,
        prolactin_level=input.prolactin_level,
        # Gas sensor data
        co2_ppm=input.co2_ppm,
        co_ppm=input.co_ppm,
        no2_ppb=input.no2_ppb,
        o3_ppb=input.o3_ppb,
        pm25_ugm3=input.pm25_ugm3,
        pm10_ugm3=input.pm10_ugm3,
        temperature_c=input.temperature_c,
        humidity_pct=input.humidity_pct,
        air_quality_index=input.air_quality_index,
        air_quality_category=input.air_quality_category,
        # TCS230 Color sensor data
        color_red=input.color_red,
        color_green=input.color_green,
        color_blue=input.color_blue,
        color_clear=input.color_clear,
        color_hue=input.color_hue,
        color_saturation=input.color_saturation,
        color_brightness=input.color_brightness,
        color_temperature=input.color_temperature,
        color_category=input.color_category
    )
@router.get("/analysis/{user_email}")
def analyze_user(user_email: str):
    from app.services.analytics_service import compute_summary
    return compute_summary(user_email)

@router.get("/gas-sensor/latest")
async def get_latest_gas_sensor_data():
    """Fetch the latest gas sensor data from ThingSpeak"""
    gas_data = await thingspeak_service.fetch_latest_gas_data()
    if gas_data:
        # Calculate AQI
        aqi_data = thingspeak_service.get_air_quality_index(gas_data)
        gas_data.update(aqi_data)
    return gas_data

@router.get("/gas-sensor/historical")
async def get_historical_gas_sensor_data(results: int = 10):
    """Fetch historical gas sensor data from ThingSpeak"""
    return await thingspeak_service.fetch_historical_gas_data(results)

@router.post("/gas-sensor/add-reading")
async def add_gas_sensor_reading(user_email: str):
    """Fetch latest gas sensor data and add it as a reading for the user"""
    gas_data = await thingspeak_service.fetch_latest_gas_data()
    if not gas_data:
        return {"error": "Failed to fetch gas sensor data from ThingSpeak"}
    
    # Calculate AQI
    aqi_data = thingspeak_service.get_air_quality_index(gas_data)
    gas_data.update(aqi_data)
    
    # Add the reading with sensor data (gas + color)
    reading = data_service.add_single_reading(
        user_email=user_email,
        flow_ml=0.0,  # Default flow value
        # Gas sensor data
        co2_ppm=gas_data.get("co2_ppm"),
        co_ppm=gas_data.get("co_ppm"),
        no2_ppb=gas_data.get("no2_ppb"),
        o3_ppb=gas_data.get("o3_ppb"),
        pm25_ugm3=gas_data.get("pm25_ugm3"),
        pm10_ugm3=gas_data.get("pm10_ugm3"),
        temperature_c=gas_data.get("temperature_c"),
        humidity_pct=gas_data.get("humidity_pct"),
        air_quality_index=gas_data.get("aqi"),
        air_quality_category=gas_data.get("category"),
        # TCS230 Color sensor data
        color_red=gas_data.get("color_red"),
        color_green=gas_data.get("color_green"),
        color_blue=gas_data.get("color_blue"),
        color_clear=gas_data.get("color_clear"),
        color_hue=gas_data.get("color_hue"),
        color_saturation=gas_data.get("color_saturation"),
        color_brightness=gas_data.get("color_brightness"),
        color_temperature=gas_data.get("color_temperature"),
        color_category=gas_data.get("color_category")
    )
    
    return {
        "message": "Gas sensor reading added successfully",
        "reading_id": reading.id,
        "gas_data": gas_data
    }