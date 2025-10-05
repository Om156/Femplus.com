import pandas as pd
import numpy as np

EXPECTED_FEATURES = [
    "flow_ml", "hb", "ph", "crp", "hba1c_ratio",
    "clots_score", "fsh_level", "lh_level",
    "amh_level", "tsh_level", "prolactin_level"
]

LABELS = [
    "Normal",
    "Anemia Risk",
    "Diabetes Risk",
    "Infection Suspected",
    "Menorrhagia",
    "PCOS Risk",
    "Thyroid Imbalance"
]

rows = []
for _ in range(1000):
    row = {f: np.random.uniform(0, 15) for f in EXPECTED_FEATURES}

    if row["hb"] < 10:
        label = "Anemia Risk"
    elif row["hba1c_ratio"] > 6.5:
        label = "Diabetes Risk"
    elif row["crp"] > 5:
        label = "Infection Suspected"
    elif row["flow_ml"] > 80 or row["clots_score"] > 5:
        label = "Menorrhagia"
    elif row["fsh_level"] > 10 and row["lh_level"] > 10 and row["amh_level"] > 5:
        label = "PCOS Risk"
    elif row["tsh_level"] > 4.5:
        label = "Thyroid Imbalance"
    else:
        label = "Normal"

    row["label"] = label
    rows.append(row)

df = pd.DataFrame(rows)
df.to_csv("app/ml/synthetic_flow_data.csv", index=False)
print("Synthetic dataset with 1000 rows created: app/ml/synthetic_flow_data.csv")
