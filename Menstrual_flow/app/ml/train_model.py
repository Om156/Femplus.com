import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

EXPECTED_FEATURES = [
    "flow_ml", "hb", "ph", "crp", "hba1c_ratio",
    "clots_score", "fsh_level", "lh_level",
    "amh_level", "tsh_level", "prolactin_level",
    "esr", "leukocyte_count", "vaginal_ph", "ca125", "estrogen", "progesterone", "androgens", "blood_glucose", "wbc_count",
    "pain_score", "weight_gain", "acne_severity", "insulin_resistance", "fever", "tenderness", "pain_during_intercourse", "bloating", "weight_loss", "appetite_loss", "vaginal_discharge", "discharge_odor", "discharge_color"
]

df = pd.read_csv("app/ml/synthetic_flow_dataset.csv")

X = df[EXPECTED_FEATURES].values
y = df["label"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

joblib.dump(model, "app/ml/model.joblib")

print("Model trained and saved to app/ml/model.joblib")
print("Training accuracy:", model.score(X_train, y_train))
print("Testing accuracy:", model.score(X_test, y_test))
