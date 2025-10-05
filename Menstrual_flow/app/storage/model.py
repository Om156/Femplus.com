from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint('email', name='uq_users_email'),)

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    blood_group = Column(String, nullable=True)
    is_verified = Column(Integer, default=0)  # 0/1
    otp_code = Column(String, nullable=True)
    otp_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=True, index=True)
    context_type = Column(String, nullable=True)  # home, feature, labs, shop, analysis
    context_id = Column(String, nullable=True)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class FlowReading(Base):
    __tablename__ = "flow_readings"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    cycle_id = Column(String, default="unknown")
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    flow_ml = Column(Float, default=0.0)
    hb = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    crp = Column(Float, nullable=True)
    hba1c_ratio = Column(Float, nullable=True)
    clots_score = Column(Float, nullable=True)
    fsh_level = Column(Float)
    lh_level = Column(Float)
    amh_level = Column(Float)
    tsh_level = Column(Float)
    prolactin_level = Column(Float)
    
    # Gas sensor data from ThingSpeak
    co2_ppm = Column(Float, nullable=True)
    co_ppm = Column(Float, nullable=True)
    no2_ppb = Column(Float, nullable=True)
    o3_ppb = Column(Float, nullable=True)
    pm25_ugm3 = Column(Float, nullable=True)
    pm10_ugm3 = Column(Float, nullable=True)
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    air_quality_index = Column(Float, nullable=True)
    air_quality_category = Column(String, nullable=True)
    
    # TCS230 Color sensor data
    color_red = Column(Float, nullable=True)
    color_green = Column(Float, nullable=True)
    color_blue = Column(Float, nullable=True)
    color_clear = Column(Float, nullable=True)
    color_hue = Column(Float, nullable=True)
    color_saturation = Column(Float, nullable=True)
    color_brightness = Column(Float, nullable=True)
    color_temperature = Column(Float, nullable=True)
    color_category = Column(String, nullable=True)
    
    # Additional parameters for comprehensive menstrual health diagnosis
    esr = Column(Float, nullable=True)  # Erythrocyte Sedimentation Rate
    leukocyte_count = Column(Float, nullable=True)  # White Blood Cell count
    vaginal_ph = Column(Float, nullable=True)  # Vaginal pH (separate from general pH)
    ca125 = Column(Float, nullable=True)  # CA-125 tumor marker
    estrogen = Column(Float, nullable=True)  # Estradiol/E2
    progesterone = Column(Float, nullable=True)  # Progesterone levels
    androgens = Column(Float, nullable=True)  # Testosterone levels
    blood_glucose = Column(Float, nullable=True)  # Fasting blood glucose
    wbc_count = Column(Float, nullable=True)  # White Blood Cell count (alternative)
    
    # Disease-specific symptom tracking
    pain_score = Column(Float, nullable=True)  # Pain intensity (0-10)
    weight_gain = Column(Float, nullable=True)  # Weight change in kg
    acne_severity = Column(Float, nullable=True)  # Acne severity score (0-5)
    insulin_resistance = Column(Float, nullable=True)  # HOMA-IR score
    fever = Column(Float, nullable=True)  # Temperature in Celsius
    tenderness = Column(Integer, nullable=True)  # Tenderness score (0-3)
    pain_during_intercourse = Column(Integer, nullable=True)  # 0/1 boolean
    bloating = Column(Integer, nullable=True)  # 0/1 boolean
    weight_loss = Column(Float, nullable=True)  # Weight loss in kg
    appetite_loss = Column(Integer, nullable=True)  # 0/1 boolean
    vaginal_discharge = Column(String, nullable=True)  # Description of discharge
    discharge_odor = Column(String, nullable=True)  # Odor description
    discharge_color = Column(String, nullable=True)  # Color description