import pandas as pd

df = pd.read_csv("app/ml/realistic_synthetic_flow_data_5000.csv")

def assign_label(row):
    if row["hb"] < 11 and row["flow_ml"] > 80:
        return "Anemia Risk"
    elif row["hba1c_ratio"] > 6.5:
        return "Diabetes Risk"
    elif row["crp"] > 6:
        return "Infection Suspected"
    elif row["flow_ml"] > 120 and row["clots_score"] > 2:
        return "Menorrhagia"
    elif (row["lh_level"] / (row["fsh_level"] + 1e-5)) > 2 or row["amh_level"] > 6:
        return "PCOS Risk"
    elif row["tsh_level"] < 0.4 or row["tsh_level"] > 4.0:
        return "Thyroid Imbalance"
    else:
        return "Normal"

df["label"] = df.apply(assign_label, axis=1)

df.to_csv("app/ml/flow_data_labeled.csv", index=False)
print("Dataset relabeled and saved as flow_data_labeled.csv")
