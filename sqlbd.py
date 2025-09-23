# init_db.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect("claims.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    claim_ref TEXT UNIQUE NOT NULL,
    phone INTEGER,
    email TEXT,
    branch TEXT,
    policy_number TEXT NOT NULL,
    plate_number INTEGER NOT NULL,
    date_of_accident DATE,
    time_of_accident TIME,
    type_of_accident TEXT,
    fatality TEXT,
    fatality_details TEXT, 
    injuries TEXT,
    location TEXT,
    legal_authority_contacted TEXT,
    police_report_number TEXT,
    witnesses TEXT,
    description_of_accident TEXT,
    image_path TEXT  -- Stores path to saved image
)
""")

conn.commit()
conn.close()
print("✅ Database and table created!")

def save_claim_to_db(name, policy_number, plate_number, location, image_path, branch, date_of_accident):
    claim_ref = f"claim_{date_of_accident.now().strftime('%Y%m%d_%H%M%S')}"
    
    conn = sqlite3.connect("claims.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO claims (
        name, claim_ref, branch, policy_number,
        plate_number, date_of_accident, location, image_path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", [
    name, claim_ref, branch, policy_number,
    plate_number, date_of_accident.isoformat(),
    location, image_path
])
    
    conn.commit()
    conn.close()
    
    return claim_ref