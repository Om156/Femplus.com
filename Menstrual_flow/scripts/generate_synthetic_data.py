import pandas as pd
import numpy as np

EXPECTED_FEATURES = [
    "flow_ml", "hb", "ph", "crp", "hba1c_ratio",
    "clots_score", "fsh_level", "lh_level",
    "amh_level", "tsh_level", "prolactin_level"
]

# Generate 1000 realistic synthetic rows
data = []
for _ in range(1000):
    row = [
        round(np.random.uniform(20, 80), 1),   # flow_ml (ml)
        round(np.random.uniform(8, 15), 1),    # hb (g/dL)
        round(np.random.uniform(4.5, 7.5), 1), # ph
        round(np.random.uniform(0, 10), 1),    # crp (mg/L)
        round(np.random.uniform(4, 7), 2),     # hba1c_ratio (%)
        round(np.random.uniform(0, 5), 1),     # clots_score
        round(np.random.uniform(2, 15), 1),    # fsh_level (mIU/mL)
        round(np.random.uniform(2, 15), 1),    # lh_level (mIU/mL)
        round(np.random.uniform(0.5, 6), 1),   # amh_level (ng/mL)
        round(np.random.uniform(0.5, 5), 1),   # tsh_level (µIU/mL)
        round(np.random.uniform(1, 25), 1)     # prolactin_level (ng/mL)
    ]
    label = np.random.choice(["Normal", "Abnormal"])
    data.append(row + [label])

df = pd.DataFrame(data, columns=EXPECTED_FEATURES + ["label"])
df.to_csv("swasthya_flow_synthetic_1000.csv", index=False)
print("Synthetic CSV created: swasthya_flow_synthetic_1000.csv")
