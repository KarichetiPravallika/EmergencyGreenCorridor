import sqlite3

conn = sqlite3.connect("emergency.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS emergency_requests (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ambulance_number TEXT,
    driver_name TEXT,
    mobile_number TEXT,
    patient_name TEXT,
    patient_age INTEGER,
    emergency_type TEXT,
    current_location TEXT,
    destination_hospital TEXT,
    distance INTEGER,
    notes TEXT,

    status TEXT DEFAULT 'Pending'

)
""")

conn.commit()
conn.close()

print("Database created successfully!")