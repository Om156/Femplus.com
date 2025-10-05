import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from PIL import Image
from io import BytesIO
import base64
import sqlite3
import pandas as pd

try:
    model = joblib.load("app/ml/model.joblib")
except Exception as e:
    print("Model loading failed:", e)
    model = RandomForestClassifier(n_estimators=100)

conn = sqlite3.connect("swasthya_flow.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS flow_data (
    flow_ml REAL, hb REAL, ph REAL, crp REAL, hba1c_ratio REAL,
    clots_score REAL, fsh_level REAL, lh_level REAL,
    amh_level REAL, tsh_level REAL, prolactin_level REAL,
    esr REAL, leukocyte_count REAL, vaginal_ph REAL, ca125 REAL, estrogen REAL,
    progesterone REAL, androgens REAL, blood_glucose REAL, wbc_count REAL,
    pain_score REAL, weight_gain REAL, acne_severity REAL, insulin_resistance REAL,
    fever REAL, tenderness REAL, pain_during_intercourse REAL, bloating REAL, weight_loss REAL,
    appetite_loss REAL, vaginal_discharge REAL, discharge_odor REAL, discharge_color REAL,
    label TEXT
)
""")
conn.commit()
conn.close()

EXPECTED_FEATURES = [
    "flow_ml", "hb", "ph", "crp", "hba1c_ratio",
    "clots_score", "fsh_level", "lh_level",
    "amh_level", "tsh_level", "prolactin_level",
    # Additional parameters for comprehensive diagnosis
    "esr", "leukocyte_count", "vaginal_ph", "ca125", "estrogen", 
    "progesterone", "androgens", "blood_glucose", "wbc_count",
    # Disease-specific symptoms
    "pain_score", "weight_gain", "acne_severity", "insulin_resistance",
    "fever", "tenderness", "pain_during_intercourse", "bloating",
    "weight_loss", "appetite_loss", "vaginal_discharge", "discharge_odor", "discharge_color"
]

def predict_flow_risk(features: dict, image_base64=None):
    # 1. Prepare features
    input_row = [float(features.get(f, 0)) for f in EXPECTED_FEATURES]
    input_data = np.array([input_row], dtype=float)

    if image_base64:
        try:
            img_data = base64.b64decode(image_base64)
            img = Image.open(BytesIO(img_data)).convert("RGB").resize((128,128))
            img_array = np.array(img).flatten()/255.0
            # Concatenate image features if needed (model must be trained for this!)
            input_data = np.hstack([input_data, img_array.reshape(1, -1)])
        except Exception as e:
            print("Image processing failed:", e)

    try:
        preds = model.predict(input_data)
        probs = model.predict_proba(input_data)
        labels = model.classes_
        prob_dict = {labels[i]: float(probs[0][i]) for i in range(len(labels))}
    except Exception as e:
        return {"prediction": "Error", "probabilities": {}, "risk_indicator": "Unknown", "advice": [str(e)], "detected_conditions": []}

    # Multi-disease detection logic
    detected_conditions = detect_multiple_conditions(features, prob_dict)
    
    # Overall risk assessment
    overall_risk = assess_overall_risk(detected_conditions, prob_dict)
    
    # Generate comprehensive advice for all detected conditions
    comprehensive_advice = generate_comprehensive_advice(detected_conditions, overall_risk, features)

    return {
        "prediction": preds[0],  # Primary prediction
        "probabilities": prob_dict,
        "risk_indicator": overall_risk,
        "advice": comprehensive_advice,
        "detected_conditions": detected_conditions
    }

def generate_advice(prediction, risk):
    """
    Returns advice strings tailored to the predicted risk/disease.
    """
    advice = []

    ############ Condition-specific health advice ########
    if prediction == "Infection Suspected":
        advice.append("Your CRP levels and flow pattern suggest possible infection.")
        advice.append("Consult a gynecologist or physician for infection screening (e.g., UTI, pelvic infection).")
        advice.append("Maintain good hygiene and stay hydrated.")
        advice.append("Avoid self-medication and seek professional care.")
        advice.append("Consider a urine test to rule out infections.")
        advice.append("Follow up with your doctor if symptoms persist.")
        advice.append("Keep track of any new symptoms or changes in your condition.")

    elif prediction == "Anemia Risk":
        advice.append("Low hemoglobin and heavy menstrual flow suggest anemia risk.")
        advice.append("Include iron-rich foods like spinach, beetroot, lentils, and red meat in your diet.")
        advice.append("Consider iron supplements if advised by a doctor.")
        advice.append("Schedule a CBC (Complete Blood Count) test to confirm.")
        advice.append("Keep track of any new symptoms or changes in your condition.")
        advice.append("Consider a nutritionist for dietary advice.")
        advice.append("Stay hydrated and maintain a balanced diet.")

    elif prediction == "PCOS Risk":
        advice.append("Hormonal imbalance indicates possible PCOS (Polycystic Ovary Syndrome).")
        advice.append("Track your menstrual cycles and maintain a healthy weight.")
        advice.append("Consult a gynecologist for ultrasound and hormone profile testing.")
        advice.append("Try stress-reduction techniques like yoga or meditation.")
        advice.append("Maintain a healthy diet and exercise regularly.")
        advice.append("Do regular health check-ups.")
        advice.append("Consider a mental health professional if experiencing mood swings.")
        advice.append("Keep track of any new symptoms or changes in your condition.")

    elif prediction == "Thyroid Imbalance":
        advice.append("Abnormal TSH values suggest thyroid imbalance.")
        advice.append("Schedule a thyroid profile test (T3, T4, TSH).")
        advice.append("Consult an endocrinologist for proper evaluation.")
        advice.append("Maintain a balanced diet and avoid excessive stress.")
        advice.append("Focus on whole foods, including fresh vegetables, fruits, lean proteins, and whole grains.")
        advice.append("Limit or avoid excessive intake of soy products, cruciferous vegetables (like broccoli and cabbage), and foods high in fiber, as these can interfere with thyroid medication absorption.")

    elif prediction == "Diabetes Risk":
        advice.append("Elevated HbA1c levels indicate poor blood sugar control.")
        advice.append("Maintain a low-sugar, high-fiber diet with regular exercise.")
        advice.append("Consult a doctor for a fasting glucose or OGTT test.")
        advice.append("Monitor your blood sugar levels regularly.")

    elif prediction == "Menorrhagia":
        advice.append("Excessive flow volume and clots suggest Menorrhagia (heavy menstrual bleeding).")
        advice.append("Monitor the number of pads/tampons used per day.")
        advice.append("Consult a gynecologist for ultrasound and blood tests.")
        advice.append("Consider iron supplements to prevent anemia.")

    elif prediction == "Normal":
        advice.append("Your results appear normal. Maintain a healthy lifestyle.")
        advice.append("Continue tracking your cycle for better predictions.")
        advice.append("Stay hydrated and practice regular exercise or yoga.")
        advice.append("Monitor any unusual changes and consult a doctor if needed.")

    ########### RISK level ############ 
    if risk == "High":
        advice.insert(0, "Your risk level is HIGH. Immediate medical consultation is advised.")
    elif risk == "Moderate":
        advice.insert(0, "Your risk level is MODERATE. Monitor closely and take preventive steps.")
    else:
        advice.insert(0, "Your risk level is LOW. Keep maintaining a healthy lifestyle.")

    return advice

def detect_multiple_conditions(features: dict, prob_dict: dict):
    """
    Detect multiple conditions based on biomarker thresholds and probabilities.
    Returns a list of detected conditions with their risk levels.
    """
    detected = []
    
    # Define condition detection thresholds based on medical literature
    conditions = {
        "PCOS/PCOD Risk": {
            "lh_level": {"min": 15, "weight": 0.25},  # LH > 15 mIU/mL
            "fsh_level": {"max": 8, "weight": 0.2},   # FSH < 8 mIU/mL (LH:FSH ratio >2:1)
            "amh_level": {"min": 4.0, "weight": 0.25}, # AMH > 4 ng/mL (very high)
            "androgens": {"min": 80, "weight": 0.15}, # Testosterone > 80 ng/dL
            "blood_glucose": {"min": 100, "weight": 0.1}, # Insulin resistance
            "weight_gain": {"min": 5, "weight": 0.05}  # Weight gain
        },
        "PID Risk": {
            "crp": {"min": 10, "weight": 0.3},        # CRP > 10 mg/L
            "wbc_count": {"min": 11000, "weight": 0.25}, # WBC > 11,000 /µL
            "fever": {"min": 37.5, "weight": 0.2},    # Fever > 37.5°C
            "vaginal_ph": {"max": 4.5, "weight": 0.15}, # Vaginal pH < 4.5
            "tenderness": {"min": 2, "weight": 0.1}   # Pelvic tenderness
        },
        "Endometriosis Risk": {
            "estrogen": {"min": 350, "weight": 0.3},   # Estrogen > 350 pg/mL
            "ca125": {"min": 35, "weight": 0.25},      # CA-125 > 35 U/mL
            "pain_score": {"min": 7, "weight": 0.25},  # Pain score > 7/10
            "pain_during_intercourse": {"min": 1, "weight": 0.2} # Dyspareunia
        },
        "Ovarian Cancer Risk": {
            "ca125": {"min": 35, "weight": 0.4},       # CA-125 > 35 U/mL
            "weight_loss": {"min": 5, "weight": 0.2},  # Unexplained weight loss
            "bloating": {"min": 1, "weight": 0.2},     # Persistent bloating
            "appetite_loss": {"min": 1, "weight": 0.2} # Loss of appetite
        },
        "Anemia Risk": {
            "hb": {"max": 12, "weight": 0.6},          # Hemoglobin < 12 g/dL
            "flow_ml": {"min": 80, "weight": 0.4}      # Heavy flow > 80ml
        },
        "Thyroid Imbalance": {
            "tsh_level": {"min": 4.0, "weight": 0.4},  # TSH > 4.0 mIU/mL (hypothyroid)
            "tsh_level_hyper": {"max": 0.4, "weight": 0.4}, # TSH < 0.4 mIU/mL (hyperthyroid)
            "prolactin_level": {"min": 20, "weight": 0.2} # Prolactin > 20 ng/mL
        },
        "Diabetes Risk": {
            "blood_glucose": {"min": 126, "weight": 0.5}, # Fasting glucose > 126 mg/dL
            "hba1c_ratio": {"min": 6.5, "weight": 0.5}   # HbA1c > 6.5%
        },
        "Infection/Inflammation": {
            "crp": {"min": 5, "weight": 0.3},          # CRP > 5 mg/L
            "esr": {"min": 20, "weight": 0.25},        # ESR > 20 mm/hr
            "wbc_count": {"min": 11000, "weight": 0.25}, # WBC > 11,000 /µL
            "vaginal_ph": {"max": 5.0, "weight": 0.2}  # Abnormal vaginal pH
        },
        "Menorrhagia": {
            "flow_ml": {"min": 80, "weight": 0.5},     # Flow > 80ml
            "clots_score": {"min": 3, "weight": 0.3},  # Heavy clots
            "pain_score": {"min": 6, "weight": 0.2}    # Pain during flow
        }
    }
    
    for condition_name, thresholds in conditions.items():
        risk_score = 0
        total_weight = 0
        matched_biomarkers = 0
        
        for biomarker, criteria in thresholds.items():
            if biomarker in features:
                value = float(features[biomarker])
                weight = criteria["weight"]
                
                # Check if biomarker meets condition criteria
                if "min" in criteria and value >= criteria["min"]:
                    risk_score += weight
                    matched_biomarkers += 1
                elif "max" in criteria and value <= criteria["max"]:
                    risk_score += weight
                    matched_biomarkers += 1
                
                total_weight += weight
        
        # Calculate final score only if at least 40% of biomarkers match (more lenient)
        if total_weight > 0 and matched_biomarkers >= len(thresholds) * 0.4:
            final_score = risk_score / total_weight
            
            # Determine risk level with more lenient thresholds
            if final_score >= 0.7:
                risk_level = "High"
            elif final_score >= 0.5:
                risk_level = "Moderate"
            elif final_score >= 0.3:
                risk_level = "Low"
            else:
                continue  # Skip conditions with very low risk
            
            # Add probability-based confidence
            prob_confidence = prob_dict.get(condition_name, 0)
            
            # Only include if biomarker risk is significant OR model has moderate confidence
            if final_score > 0.3 or prob_confidence > 0.2:
                detected.append({
                    "condition": condition_name,
                    "risk_level": risk_level,
                    "confidence": max(final_score, prob_confidence),
                    "biomarkers": {k: float(features.get(k, 0)) for k in thresholds.keys() if k in features},
                    "matched_count": matched_biomarkers,
                    "total_count": len(thresholds)
                })
    
    # Sort by confidence (highest first)
    detected.sort(key=lambda x: x["confidence"], reverse=True)
    
    return detected

def assess_overall_risk(detected_conditions: list, prob_dict: dict):
    """
    Assess overall risk level based on detected conditions.
    """
    if not detected_conditions:
        return "Low"
    
    # Count high-risk conditions
    high_risk_count = sum(1 for cond in detected_conditions if cond["risk_level"] == "High")
    moderate_risk_count = sum(1 for cond in detected_conditions if cond["risk_level"] == "Moderate")
    
    # Determine overall risk
    if high_risk_count >= 2:
        return "Critical"
    elif high_risk_count >= 1:
        return "High"
    elif moderate_risk_count >= 2:
        return "Moderate"
    elif moderate_risk_count >= 1:
        return "Low-Moderate"
    else:
        return "Low"

def analyze_biomarkers(features: dict):
    """
    Analyze individual biomarkers and provide specific feedback.
    """
    analysis = []
    
    # CRP Analysis
    crp = float(features.get('crp', 0))
    if crp > 10:
        analysis.append(f"🔴 CRP is HIGH ({crp:.1f}) - Possible infection or inflammation")
    elif crp > 5:
        analysis.append(f"🟡 CRP is ELEVATED ({crp:.1f}) - Mild inflammation")
    else:
        analysis.append(f"🟢 CRP is NORMAL ({crp:.1f})")
    
    # Hemoglobin Analysis
    hb = float(features.get('hb', 0))
    if hb < 12:
        analysis.append(f"🔴 Hemoglobin is LOW ({hb:.1f}) - Possible anemia")
    elif hb < 13:
        analysis.append(f"🟡 Hemoglobin is BORDERLINE ({hb:.1f}) - Monitor closely")
    else:
        analysis.append(f"🟢 Hemoglobin is NORMAL ({hb:.1f})")
    
    # pH Analysis
    ph = float(features.get('ph', 0))
    if ph < 4.5:
        analysis.append(f"🔴 pH is LOW ({ph:.1f}) - Possible infection")
    elif ph < 5.0:
        analysis.append(f"🟡 pH is BORDERLINE ({ph:.1f}) - Monitor")
    else:
        analysis.append(f"🟢 pH is NORMAL ({ph:.1f})")
    
    # HbA1c Analysis
    hba1c = float(features.get('hba1c_ratio', 0))
    if hba1c > 6.5:
        analysis.append(f"🔴 HbA1c is HIGH ({hba1c:.1f}%) - Diabetes risk")
    elif hba1c > 5.7:
        analysis.append(f"🟡 HbA1c is ELEVATED ({hba1c:.1f}%) - Pre-diabetes")
    else:
        analysis.append(f"🟢 HbA1c is NORMAL ({hba1c:.1f}%)")
    
    # Flow Analysis
    flow = float(features.get('flow_ml', 0))
    if flow > 100:
        analysis.append(f"🔴 Flow is HEAVY ({flow:.1f}ml) - Menorrhagia risk")
    elif flow > 60:
        analysis.append(f"🟡 Flow is MODERATE ({flow:.1f}ml) - Monitor")
    else:
        analysis.append(f"🟢 Flow is NORMAL ({flow:.1f}ml)")
    
    # TSH Analysis
    tsh = float(features.get('tsh_level', 0))
    if tsh > 4.0:
        analysis.append(f"🔴 TSH is HIGH ({tsh:.1f}) - Thyroid dysfunction")
    elif tsh < 0.4:
        analysis.append(f"🔴 TSH is LOW ({tsh:.1f}) - Hyperthyroidism")
    else:
        analysis.append(f"🟢 TSH is NORMAL ({tsh:.1f})")
    
    # Clots Analysis
    clots = float(features.get('clots_score', 0))
    if clots > 3:
        analysis.append(f"🔴 Clots are HEAVY ({clots:.1f}) - Possible menorrhagia")
    elif clots > 1:
        analysis.append(f"🟡 Clots are MODERATE ({clots:.1f}) - Monitor")
    else:
        analysis.append(f"🟢 Clots are NORMAL ({clots:.1f})")
    
    # FSH Analysis
    fsh = float(features.get('fsh_level', 0))
    if fsh > 8:
        analysis.append(f"🔴 FSH is HIGH ({fsh:.1f}) - Possible PCOS")
    else:
        analysis.append(f"🟢 FSH is NORMAL ({fsh:.1f})")
    
    # LH Analysis
    lh = float(features.get('lh_level', 0))
    if lh > 12:
        analysis.append(f"🔴 LH is HIGH ({lh:.1f}) - Possible PCOS")
    else:
        analysis.append(f"🟢 LH is NORMAL ({lh:.1f})")
    
    # Prolactin Analysis
    prolactin = float(features.get('prolactin_level', 0))
    if prolactin > 20:
        analysis.append(f"🔴 Prolactin is HIGH ({prolactin:.1f}) - Thyroid issue")
    else:
        analysis.append(f"🟢 Prolactin is NORMAL ({prolactin:.1f})")
    
    # ESR Analysis
    esr = float(features.get('esr', 0))
    if esr > 20:
        analysis.append(f"🔴 ESR is ELEVATED ({esr:.1f}) - Possible inflammation")
    else:
        analysis.append(f"🟢 ESR is NORMAL ({esr:.1f})")
    
    # WBC Analysis
    wbc = float(features.get('wbc_count', 0))
    if wbc > 11000:
        analysis.append(f"🔴 WBC is HIGH ({wbc:.0f}) - Possible infection")
    elif wbc < 4000:
        analysis.append(f"🟡 WBC is LOW ({wbc:.0f}) - Immunosuppression risk")
    else:
        analysis.append(f"🟢 WBC is NORMAL ({wbc:.0f})")
    
    # CA-125 Analysis
    ca125 = float(features.get('ca125', 0))
    if ca125 > 35:
        analysis.append(f"🔴 CA-125 is ELEVATED ({ca125:.1f}) - Endometriosis/Cancer risk")
    else:
        analysis.append(f"🟢 CA-125 is NORMAL ({ca125:.1f})")
    
    # Estrogen Analysis
    estrogen = float(features.get('estrogen', 0))
    if estrogen > 350:
        analysis.append(f"🔴 Estrogen is HIGH ({estrogen:.1f}) - Endometriosis risk")
    elif estrogen < 50:
        analysis.append(f"🟡 Estrogen is LOW ({estrogen:.1f}) - Menopause/ovarian failure")
    else:
        analysis.append(f"🟢 Estrogen is NORMAL ({estrogen:.1f})")
    
    # Blood Glucose Analysis
    glucose = float(features.get('blood_glucose', 0))
    if glucose > 126:
        analysis.append(f"🔴 Blood Glucose is HIGH ({glucose:.1f}) - Diabetes")
    elif glucose > 100:
        analysis.append(f"🟡 Blood Glucose is ELEVATED ({glucose:.1f}) - Pre-diabetes")
    else:
        analysis.append(f"🟢 Blood Glucose is NORMAL ({glucose:.1f})")
    
    # Pain Score Analysis
    pain = float(features.get('pain_score', 0))
    if pain > 7:
        analysis.append(f"🔴 Pain is SEVERE ({pain:.1f}/10) - Medical attention needed")
    elif pain > 4:
        analysis.append(f"🟡 Pain is MODERATE ({pain:.1f}/10) - Monitor closely")
    elif pain > 0:
        analysis.append(f"🟢 Pain is MILD ({pain:.1f}/10)")
    else:
        analysis.append(f"🟢 No pain reported")
    
    return analysis

def generate_comprehensive_advice(detected_conditions: list, overall_risk: str, features: dict):
    """
    Generate comprehensive advice for all detected conditions.
    """
    advice = []
    
    # Add biomarker analysis first
    biomarker_analysis = analyze_biomarkers(features)
    advice.extend(biomarker_analysis)
    
    # Simple risk assessment
    if detected_conditions:
        if overall_risk == "Critical":
            advice.append("\n🚨 CRITICAL RISK: Multiple serious conditions detected. Seek immediate medical attention.")
        elif overall_risk == "High":
            advice.append("\n⚠️ HIGH RISK: Serious conditions detected. Consult a doctor within 24-48 hours.")
        elif overall_risk == "Moderate":
            advice.append("\n⚡ MODERATE RISK: Conditions require monitoring. Schedule a doctor visit within a week.")
        else:
            advice.append("\n📊 LOW RISK: Some conditions detected. Monitor closely and consider preventive care.")
    else:
        advice.append("\n✅ NO RISK DETECTED: You are good to go! Your biomarkers appear normal.")
    
    # Only show advice for actually detected conditions
    if detected_conditions:
        advice.append(f"\n🔍 Detected Conditions ({len(detected_conditions)}):")
        
        for condition in detected_conditions:
            condition_name = condition["condition"]
            risk_level = condition["risk_level"]
            confidence = int(condition["confidence"] * 100)
            
            advice.append(f"\n📋 {condition_name} ({risk_level} Risk - {confidence}% confidence):")
            
            if condition_name == "Anemia Risk":
                advice.extend([
                    "• Eat iron-rich foods: spinach, beetroot, lentils, red meat",
                    "• Consider iron supplements (ask doctor first)",
                    "• Get a blood test to confirm"
                ])
            elif condition_name == "PCOS Risk":
                advice.extend([
                    "• Track your menstrual cycles",
                    "• Maintain healthy weight",
                    "• See a gynecologist for testing"
                ])
            elif condition_name == "Thyroid Imbalance":
                advice.extend([
                    "• Get thyroid blood tests (T3, T4, TSH)",
                    "• See an endocrinologist",
                    "• Eat a balanced diet"
                ])
            elif condition_name == "Diabetes Risk":
                advice.extend([
                    "• Eat less sugar, more fiber",
                    "• Exercise regularly",
                    "• Get blood sugar tests",
                    "• See a diabetes specialist"
                ])
            elif condition_name == "Infection Suspected":
                advice.extend([
                    "• See a doctor immediately",
                    "• Take prescribed antibiotics",
                    "• Stay clean and hydrated"
                ])
            elif condition_name == "Menorrhagia":
                advice.extend([
                    "• Track how many pads you use",
                    "• See a gynecologist",
                    "• Consider iron supplements"
                ])
            elif condition_name == "Endometriosis Risk":
                advice.extend([
                    "• See a gynecologist for exam",
                    "• Track your pain patterns",
                    "• Consider anti-inflammatory diet"
                ])
            elif condition_name == "PID Risk":
                advice.extend([
                    "• See a doctor immediately",
                    "• Take all prescribed antibiotics",
                    "• Avoid sex until treated"
                ])
    else:
        advice.append("\n✅ No specific conditions detected. Your biomarkers appear to be within normal ranges.")
    
    # Simple general advice
    if detected_conditions:
        advice.append("\n💡 General Tips:")
        advice.extend([
            "• See your doctor regularly",
            "• Follow treatment plans",
            "• Don't ignore symptoms"
        ])
    else:
        advice.extend([
            "\n💡 Stay Healthy:",
            "• Regular check-ups",
            "• Eat well and exercise",
            "• Track your cycle"
        ])
    
    return advice

def save_user_entry(features: dict, label):
    """Save user data for future retraining."""
    try:
        conn = sqlite3.connect("swasthya_flow.db")
        c = conn.cursor()
        values = [features.get(f, 0) for f in EXPECTED_FEATURES] + [label]
        c.execute(
            f"INSERT INTO flow_data ({','.join(EXPECTED_FEATURES)}, label) VALUES ({','.join(['?']*len(values))})",
            values
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Saving user entry failed:", e)

def retrain_model_incremental():
    """Retrain the model incrementally on new user data."""
    try:
        conn = sqlite3.connect("swasthya_flow.db")
        df = pd.read_sql("SELECT * FROM flow_data", conn)
        conn.close()
        if len(df) < 10:
            return
        X = df[EXPECTED_FEATURES].values
        y = df['label'].values
        model.fit(X, y)
        joblib.dump(model, "app/ml/model.joblib")
    except Exception as e:
        print("Incremental retraining failed:", e)