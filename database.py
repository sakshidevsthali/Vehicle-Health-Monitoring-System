from sqlalchemy import create_engine, text

DATABASE_URL = "sqlite:///vehicle.db"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS vehicle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT,
            speed INTEGER,
            engine_temp INTEGER,
            fuel_level INTEGER,
            battery_voltage REAL,
            status TEXT,
            dtc_code TEXT,
            dtc_description TEXT         
        )
    """))

    conn.commit()

print("Vehicle Table Created Successfully")