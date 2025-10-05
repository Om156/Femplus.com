from app.database import SessionLocal
from app.storage.model import FlowReading


def list_all_readings(user_email: str):
    """Return all readings for a given user as list of dicts (metric/value format)."""
    session = SessionLocal()
    try:
        rows = (
            session.query(FlowReading)
            .filter(FlowReading.user_email == user_email)
            .order_by(FlowReading.timestamp)
            .all()
        )
        return [
            {
                "id": r.id,
                "user_email": r.user_email,
                "cycle_id": r.cycle_id,
                "flow_ml": r.flow_ml,
                "hb": r.hb,
                "ph": r.ph,
                "crp": r.crp,
                "hba1c_ratio": r.hba1c_ratio,
                "clots_score": r.clots_score,
                "fsh_level": r.fsh_level,
                "lh_level": r.lh_level,
                "amh_level": r.amh_level,
                "tsh_level": r.tsh_level,
                "prolactin_level": r.prolactin_level,
                # Gas sensor data
                "co2_ppm": r.co2_ppm,
                "co_ppm": r.co_ppm,
                "no2_ppb": r.no2_ppb,
                "o3_ppb": r.o3_ppb,
                "pm25_ugm3": r.pm25_ugm3,
                "pm10_ugm3": r.pm10_ugm3,
                "temperature_c": r.temperature_c,
                "humidity_pct": r.humidity_pct,
                "air_quality_index": r.air_quality_index,
                "air_quality_category": r.air_quality_category,
                # TCS230 Color sensor data
                "color_red": r.color_red,
                "color_green": r.color_green,
                "color_blue": r.color_blue,
                "color_clear": r.color_clear,
                "color_hue": r.color_hue,
                "color_saturation": r.color_saturation,
                "color_brightness": r.color_brightness,
                "color_temperature": r.color_temperature,
                "color_category": r.color_category,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in rows
        ]
    finally:
        session.close()


from datetime import datetime

def add_single_reading(
    user_email: str,
    flow_ml: float = 0.0,
    hb: float = None,
    ph: float = None,
    crp: float = None,
    hba1c_ratio: float = None,
    clots_score: float = None,
    cycle_id: str = "unknown",
    fsh_level=None, 
    lh_level=None, 
    amh_level=None,
    tsh_level=None,
    prolactin_level=None,
    # Gas sensor data
    co2_ppm: float = None,
    co_ppm: float = None,
    no2_ppb: float = None,
    o3_ppb: float = None,
    pm25_ugm3: float = None,
    pm10_ugm3: float = None,
    temperature_c: float = None,
    humidity_pct: float = None,
    air_quality_index: float = None,
    air_quality_category: str = None,
    # TCS230 Color sensor data
    color_red: float = None,
    color_green: float = None,
    color_blue: float = None,
    color_clear: float = None,
    color_hue: float = None,
    color_saturation: float = None,
    color_brightness: float = None,
    color_temperature: float = None,
    color_category: str = None
):
    session = SessionLocal()
    try:
        reading = FlowReading(
            user_email=user_email,
            flow_ml=flow_ml,
            hb=hb,
            ph=ph,
            crp=crp,
            hba1c_ratio=hba1c_ratio,
            clots_score=clots_score,
            cycle_id=cycle_id,
            fsh_level=fsh_level,
            lh_level=lh_level,
            amh_level=amh_level,
            tsh_level=tsh_level,
            prolactin_level=prolactin_level,
            # Gas sensor data
            co2_ppm=co2_ppm,
            co_ppm=co_ppm,
            no2_ppb=no2_ppb,
            o3_ppb=o3_ppb,
            pm25_ugm3=pm25_ugm3,
            pm10_ugm3=pm10_ugm3,
            temperature_c=temperature_c,
            humidity_pct=humidity_pct,
            air_quality_index=air_quality_index,
            air_quality_category=air_quality_category,
            # TCS230 Color sensor data
            color_red=color_red,
            color_green=color_green,
            color_blue=color_blue,
            color_clear=color_clear,
            color_hue=color_hue,
            color_saturation=color_saturation,
            color_brightness=color_brightness,
            color_temperature=color_temperature,
            color_category=color_category,
            timestamp=datetime.utcnow()
        )
        session.add(reading)
        session.commit()
        session.refresh(reading)
        return reading
    finally:
        session.close()
