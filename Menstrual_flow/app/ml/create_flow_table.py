import sqlite3

EXPECTED_FEATURES = [
    "flow_ml", "hb", "ph", "crp", "hba1c_ratio",
    "clots_score", "fsh_level", "lh_level",
    "amh_level", "tsh_level", "prolactin_level"
]

conn = sqlite3.connect("swasthya_flow.db")
c = conn.cursor()

columns = ", ".join([f"{f} REAL" for f in EXPECTED_FEATURES])
sql = f"""
CREATE TABLE IF NOT EXISTS flow_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {columns},
    label TEXT
)
"""
c.execute(sql)
conn.commit()
conn.close()

print("Table flow_data created (if it didn't exist).")
