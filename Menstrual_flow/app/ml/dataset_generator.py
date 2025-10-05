import numpy as np
import pandas as pd

def generate_synthetic_data(n_samples: int = 10000, random_state: int = 42) -> pd.DataFrame:
    np.random.seed(random_state)

    flow_ml = np.random.normal(loc=40, scale=20, size=n_samples).clip(0, 200)
    hb = np.random.normal(loc=12.5, scale=1.8, size=n_samples).clip(6, 18)
    ph = np.random.normal(loc=4.7, scale=0.6, size=n_samples).clip(3.0, 8.0)
    crp = np.random.normal(loc=4.0, scale=4.0, size=n_samples).clip(0, 100)
    hba1c = np.random.normal(loc=5.5, scale=0.9, size=n_samples).clip(4.0, 14.0)
    clots_score = np.random.poisson(lam=1.0, size=n_samples).clip(0, 5)

    anemia = (hb < 11.0).astype(int)
    infection = ((ph > 5.5) | (crp > 5.0)).astype(int)
    inflammation = (crp > 5.0).astype(int)
    diabetes = (hba1c >= 6.5).astype(int)
    heavy_flow = (flow_ml >= 80.0).astype(int)
    pcos = ((heavy_flow + diabetes + (clots_score >= 2).astype(int)) >= 2).astype(int)

    return pd.DataFrame({
        "flow_ml": flow_ml,
        "hb": hb,
        "ph": ph,
        "crp": crp,
        "hba1c": hba1c,
        "clots_score": clots_score,
        "label_anemia": anemia,
        "label_infection": infection,
        "label_inflammation": inflammation,
        "label_diabetes": diabetes,
        "label_pcos": pcos
    })
